from Core.utilities import RegexpReplacer
from Core.utilities import Splitter
from Core.utilities import SpellChecker
from Core.utilities import NgramHandler
from Core.constants import PURGE_TRESHOLD
from Core.services import get_tweets_for_filtering_ngrams
from Core.services import get_tweets_for_analyzing
from Core.services import get_tweets_for_pruning

from nltk.tag.sequential import ClassifierBasedPOSTagger
from nltk.corpus import treebank

mapfunc_filter = """
function() {
        this.features.raw_feature_list_neg.forEach(
    function(word) { emit(word, 1) }
  )
}
"""


reducefunc = """
function reduce(key, values) {
  return values.length;
}
"""


class TrainingSetAnalyzer():
    '''
    This class handles the setting of the training set data
    and provides support for features exctraction given a text'''

    def __init__(self, limit=300, debug=True):
        '''Instance the TrainingSetAnalyzer

        Keyword arguments:
        @param: limit size of the tweets which need to be analyzed (300)
        @param: debug flag for development process
        '''
        self.__debug = debug
        self.__limit = limit
        self.__speller = SpellChecker()
        self.__splitter = Splitter("rtw")
        self.__replacer = RegexpReplacer()
        self.__ngramHandler = NgramHandler()

        train_sents = treebank.tagged_sents()[:3000]
        self.__tagger = ClassifierBasedPOSTagger(train=train_sents)

    def __analyzeSingleTweet(self, tweet):
        '''
        Helper function to get unigrams, emoticons, ngrams given a text

        Keyword arguments:
        @param: tweet the tweet to be analyzed
        '''

        chunks = self.__splitter.split(u''+tweet)
        raw_feature_list_neg = []
        emot_list = []
        ngrams = []
        for subTweet in chunks:
            try:
                preprocessed_tweet = self.__replacer.preprocess(subTweet)
                acr_expanded, tmp_emot_list = self.__replacer \
                    .acr_emot_exctractor(preprocessed_tweet)
                emot_list += tmp_emot_list
                enanched_txt = self.__speller.check_and_replace(acr_expanded)
                tagged_sent = self.__tagger.tag(enanched_txt)
                raw_feature_list_neg += self.__replacer \
                    .filter_raw_feature_list(
                        acr_expanded)
                ngrams += self.__ngramHandler.exctract_ngrams(tagged_sent)
            except Exception as e:
                print "Sorry, something goes wrong: %s txt: %s" \
                    % (str(e), tweet)

        return raw_feature_list_neg, emot_list, ngrams

    def analyze(self):
            '''
            Analyzes a set of tweets
            '''
            print "Found %i elments for training" % self.__limit
            n = 0
            while n < 20:
                qs = get_tweets_for_analyzing(skip=n)
                for tweet in qs:
                    raw_feature_list_neg, emot, ngrams = self.__analyzeSingleTweet(
                        tweet.text)
                    if not self.__debug:
                            print "saving...."
                            tweet.set_features(raw_feature_list_neg, emot, ngrams)
                n += 1
            return

    def extract_features_for_classification(self, text):
            '''
            Helper function to exctract features given a text

            Keyword arguments:
            @param: text the text whose the features will be exctracted
            '''
            raw_feature_list_neg, emot_list, ngrams = self.__analyzeSingleTweet(
                text
            )
            return raw_feature_list_neg, emot_list, ngrams, dict(
                [(word, True) for word in raw_feature_list_neg + emot_list + ngrams])

    def purge_useless_features(self):
        '''Helper function to prune less frequent unigram features'''

        tweets = get_tweets_for_pruning()
        print "Pruning process for %i tweets" % tweets.count()
        mrt = tweets.map_reduce(mapfunc_filter, reducefunc, "cn")
        mrt = filter(lambda status: status.value > PURGE_TRESHOLD, mrt)
        purged_qs = [item.key for item in mrt]
        for tweet in tweets:
            try:
                tweet.features.filtered_unigram = [item for item in purged_qs if item in tweet.features.raw_feature_list_neg]
                tweet.save()
            except Exception, e:
                print e
        print "Done!"

    def is_objective(self, text):
        '''
        Helper to get if a text is objective or not

        Keyword arguments:
        @param: text the text which needs to be analyzed
        '''
        return self.__replacer.is_objective(text.split())

    def filter_unigrams_ngrams(self):
        '''Filters unigrams from ngrams'''

        print "Filtering unigrams-ngrams process"
        n = 0
        while n < 20:
            qs = get_tweets_for_filtering_ngrams(skip=n)
            for tweet in qs:
                print "Filtering..."
                tweet.features.raw_feature_list_neg = [
                    item for item in tweet.features.raw_feature_list_neg if item not in ' '.join(tweet.features.ngrams).split()
                ]
                print "Saving..."
                tweet.save()
            n += 1
        return

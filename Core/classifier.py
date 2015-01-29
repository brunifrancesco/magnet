from Core.models import Status
from Core.processing2 import TrainingSetAnalyzer
from Core.exceptions import MagnetException

from nltk.classify import NaiveBayesClassifier
from nltk import metrics
from nltk.classify.util import accuracy

from itertools import chain
import collections


class ExClassifier():
    '''This class provides support for all the actions,
    somehow involved in the classification process

    Features types:
    UNNN: UNigrams with negation handling
    UNNN_F: Filtered UNigrams with negation handling
    EMOT: Emoticons
    NGR: Ngrams
    '''
    def __init__(self, model):
        '''Create a new ExClassifier instance, given a RawMagnetModel
        @param: model: a RawMagnetModel instance'''

        if not model:
            raise MagnetException("No model loaded in Magnet Classifier")
        self.__features_list = model.features_list

        pos_tweets = Status.objects \
            .filter(sentiment=3) \
            .limit(model.limit/2)

        neg_tweets = Status.objects \
            .filter(sentiment=-3) \
            .limit(model.limit/2)

        if "UNNN_F" in model.features_list:
            pos_tweets.filter(features__filtered_unigram__gt=[])
            neg_tweets.filter(features__filtered_unigram__gt=[])

        if "UNNN" in model.features_list:
            pos_tweets.filter(features__raw_feature_list_neg__gt=[])
            neg_tweets.filter(features__fraw_feature_list_neg__gt=[])

        self.__tweets = list(chain(pos_tweets, neg_tweets))

    def __exctract_know_features_by_type(self, tweet):
        '''Exctracts features, given a stored tweet and a RawMagnetModel

        Keyword Arguments:
        @param: tweet: the stored tweet whose features will be exctracted

        '''

        feats = []
        if "UNNN" in self.__features_list:
            feats = [(word, True) for word in tweet.features.raw_feature_list_neg]
        if "UNNN_F" in self.__features_list:
            feats += [(word, True) for word in tweet.features.filtered_unigram]
        elif "EMOT" in self.__features_list:
            feats += [(word, True) for word in tweet.features.emoticons]
        elif "NGR" in self.__features_list:
            feats += [(word, True) for word in tweet.features.ngrams]
        return dict(feats)

    def label_feats_from_corpus(self):
        '''Append the features set, to the correct class'''

        label_feats = collections.defaultdict(list)
        i = 0
        for tweet in self.__tweets:
            if tweet.features:
                i += 1
                feats = self.__exctract_know_features_by_type(tweet)
                if(tweet.sentiment == 3):
                    label_feats["pos"].append(feats)
                elif tweet.sentiment == -3:
                    label_feats["neg"].append(feats)
        return label_feats

    def __get_elements_for_classification(self, lfeats, train_number, classifying=True):
        '''Create the train set (and eventually the test set)

        Keyword Arguments:
        @param: lfeats dict with positive and negative keys
        @param: train_number a progressive number used during the k-fold evaluation
        @param: classifying used or not in the classification process'''

        train_feats = []
        test_feats = []
        for label, feats in lfeats.iteritems():
            if classifying:
                train_feats.extend([(feat, label) for feat in feats])
            else:
                cutoff = train_number * len(feats)/10
                train_feats.extend([(feat, label) for feat in feats[:cutoff]])
                test_feats.extend([(feat, label) for feat in feats[cutoff:]])

        nb_classifier = NaiveBayesClassifier.train(train_feats)
        return train_feats, test_feats, nb_classifier

    def classify_bulk(self, texts):
        '''Classify a list of texts

        Keyword arguments:
        @param: text the list o texts to get classified
        '''

        results = []
        classifier = None
        tsa = TrainingSetAnalyzer()
        for text in texts:
            if not tsa.is_objective(text):
                if not classifier:
                    lfeats = self.label_feats_from_corpus()
                    train_feats, test_feats, classifier = self. \
                        __get_elements_for_classification(lfeats, train_number=9)
                raw_feature_list_neg, emot_list, ngrams, negfeat = tsa.extract_features_for_classification(text)
                result = classifier.classify(negfeat)
                if result == "pos":
                    results.append(dict(
                        text=text, unigrams=raw_feature_list_neg, emoticons=emot_list, ngrams=ngrams, label="Positive"
                        ))
                else:
                    results.append(dict(
                        text=text, unigrams=raw_feature_list_neg, emoticons=emot_list, ngrams=ngrams, label="Negative"
                        ))
            else:
                results.append(dict(label="Objective", text=text))
        return results

    def evaluate_accuracy(self):
        '''Evaluate accuracy given a classifer model'''

        accuracies = []
        lfeats = self.label_feats_from_corpus()
        for i in range(1, 10):
            train_feats, test_feats, nb_classifier = self\
                .__get_elements_for_classification(lfeats, train_number=i, classifying=False)
            accuracies.append(accuracy(nb_classifier, test_feats))
        return sum(accuracies)/len(accuracies)

    def evaluate_precision_recall_f_measure(self):
        '''Evaluate precision, recall and f1 measure'''

        scores = dict(prec_pos=[], rec_pos=[], fmeas_pos=[], prec_neg=[], rec_neg=[], fmeas_neg=[])
        lfeats = self.label_feats_from_corpus()
        for i in range(1, 10):
            train_feats, test_feats, nb_classifier = self\
                .__get_elements_for_classification(lfeats, train_number=i, classifying=False)
            refsets = collections.defaultdict(set)
            testsets = collections.defaultdict(set)
            for i, (feats, label) in enumerate(test_feats):
                refsets[label].add(i)
                observed = nb_classifier.classify(feats)
                testsets[observed].add(i)
            precisions = {}
            recalls = {}
            f_measure = {}
            for label in nb_classifier.labels():
                precisions[label] = metrics.precision(
                    refsets[label], testsets[label]
                )
                recalls[label] = metrics.recall(refsets[label], testsets[label])
                f_measure[label] = metrics.f_measure(
                    refsets[label], testsets[label]
                )
            #print nb_classifier.show_most_informative_features(n=20)
            scores["prec_pos"].append(precisions["pos"])
            scores["prec_neg"].append(precisions["neg"])

            scores["rec_pos"].append(recalls["pos"])
            scores["rec_neg"].append(recalls["neg"])

            scores["fmeas_pos"].append(f_measure["pos"])
            scores["fmeas_neg"].append(f_measure["neg"])

        scores["prec_pos"] = sum(scores["prec_pos"]) / len(scores["prec_pos"])
        scores["prec_neg"] = sum(scores["prec_neg"]) / len(scores["prec_neg"])

        scores["rec_pos"] = sum(scores["rec_pos"]) / len(scores["rec_pos"])
        scores["rec_neg"] = sum(scores["rec_neg"]) / len(scores["rec_neg"])

        scores["fmeas_pos"] = sum(scores["fmeas_pos"]) / len(scores["fmeas_pos"])
        scores["fmeas_neg"] = sum(scores["fmeas_neg"]) / len(scores["fmeas_neg"])
        return scores

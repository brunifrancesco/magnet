import re

from nltk.corpus import wordnet
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from nltk.chunk import RegexpParser

from Core.env_set import PolarWordsEnvSetter
from Core.env_set import AcronymsEnvSetter
from Core.env_set import EmoticonEnvSetter
from Core.constants import CHUNK_RULE
from Core.constants import CONTRACTIONS_PATTERNS
from Core.constants import GENERAL_PATTERNS
from Core.constants import RTW_SPLIT_PATTERN
from Core.constants import CUSTOMPATTERNS


def singleton(cls):
        '''Helper function to keep trace of the instanciated objects'''
        instances = {}

        def getinstance():
                if cls not in instances:
                    instances[cls] = cls()
                return instances[cls]

        return getinstance


@singleton
class EnvClass:
        '''This singleton (and factory) class is used to share common objects in this module'''

        def __init__(self):
                self.polar_words = PolarWordsEnvSetter().load_from_pickle(
                    join=True
                )
                self.stemmer = SnowballStemmer("english")


class RegexpReplacer():
    '''Helper class which works with regex patterns. Handles part of the preprocessing step'''

    def __init__(self):
	
        self.__polar_words = EnvClass().polar_words
        self.__stemmer = EnvClass().stemmer

        self.__acronyms = AcronymsEnvSetter().load_from_pickle()
        self.__emot = EmoticonEnvSetter().load_from_pickle()
        self.__pre_process_patterns = [
            (re.compile(regex, re.IGNORECASE), repl) for (regex, repl) in
            CONTRACTIONS_PATTERNS+GENERAL_PATTERNS
        ]
        self.__english_stopwords = stopwords.words('english')

    def acr_emot_exctractor(self, text):
	'''
	Exctracts emoticons and expand acronysm given a text
	
	Keyword arguments:
	@param: text string whose expand acronyms and retrieve emoticons
	'''
        rec_emot = []
        for i, word in enumerate(text):
            if word.lower() in self.__acronyms.keys() and word is not None:
                text[i] = self.__acronyms[word.lower()]
            if word in self.__emot:
                rec_emot.append(word.lower())
                text[i] = None
        text = filter(lambda item: item is not None, text)
        return text, rec_emot

    def preprocess(self, text):
	'''
	Applies regex patterns given a text (identify urls, expand general contractions..)
	
	Keyword arguments:
	@param: text text string whose need to be preprocessed
	'''
        s = text
        for (pattern, repl) in self.__pre_process_patterns:
            s = re.sub(pattern, repl, s)
        return s.split()

    def filter_raw_feature_list(self, raw_feature_list):
	'''
	Gets rid of useless unigrams
	
	keyword Arguments:
	@param: raw_feature_list the list of unigrams to be filtered out
	'''

        raw_feature_list = [
            self.__stemmer.stem(item) for item in
            raw_feature_list if self.__stemmer.stem(item) in self.__polar_words
        ]
        raw_feature_list = filter(
            lambda item: item not in
            self.__english_stopwords and item not in
            CUSTOMPATTERNS, raw_feature_list
        )
        raw_feature_list = [word.lower() for word in raw_feature_list]
        return list(set(raw_feature_list))

    def is_objective(self, tokenized_text):
	'''
	Checks if a text is objective or not
	
	Keyword arguments:
	@param: tokenized_text the text to be checked out, represented as an array of words
	'''

        for word in tokenized_text:
            if self.__stemmer.stem(word) in self.__polar_words:
                return False
        return True


class Splitter():
    '''This class provides a basic method for detecting retweets in tweets'''
    def __init__(self, pattern_type):
	'''
	Instanciate the Splitter class given the pattern type

	Keyword arguments:
        @param: pattern_type the pattern whose splitting on
	'''

        if(pattern_type == "rtw"):
            pattern = RTW_SPLIT_PATTERN
        self.__patterns = re.compile(pattern)

    def split(self, text):
	'''Split the text, filtering out useless tokens
	
	Keyword arguments:
	@param text whose need to be splitted
	'''
        rtw_chunks = filter(
            lambda t: t not in ["RT", "rt", "via", "", None],
            self.__patterns.split(text))
        return rtw_chunks


class SpellChecker():
    '''This class implements a spell checking feature. 
	It tries to remove repeated letters if the words seems not correct'''
    
    def __init__(self, dict_type="en-EN"):
	'''Instanciate the SpellChecker instance, defining a dict for looking into.
	
	Keyword arguments:
	@param: dict_type the language dict whose words have looked for.
	'''

        #self.__dict = enchant.Dict(dict_type)
        self.__repeat_regexp = re.compile(r'(\w*)(\w)\2(\w*)')
        self.__repl = r'\1\2\3'

    def check_and_replace(self, text):
	'''
	Iterates over each word in the tokenized text and applies the replacing procedure
	
	Keyword arguments:
	@param: text the tokenized text whose the replacing need to be applied
	'''
        for i, word in enumerate(text):
            if not word.startswith("["):
                word = self.__replace(word)
                text[i] = word
        return text

    def __replace(self, word):
	'''
	Replaces the word with a correct one if it exists. If the passed word seems correct no further
	analysis is then implemented, else it tries to remove a repeated letter until this process 
	is available.
	In a previuos version of this function, this method tried to set a new word if the passed one 
	was completely wrong.
	Keyword arguments:
	@param: word the word whose need to be replaced or not
	'''

        if wordnet.synsets(word):
            return word
        repl_word = self.__repeat_regexp.sub(self.__repl, word)
        if repl_word != word:
            return self.__replace(repl_word)
        else:
            '''if not self.__dict.check(repl_word):
                words = self.__dict.suggest(repl_word)
                if len(words):
                    return words[0]'''
            return repl_word


class NgramHandler():
    '''This class handles the ngram detection'''

    def __init__(self):
        self.__polar_words = EnvClass().polar_words
        self.__stemmer = EnvClass().stemmer

    def exctract_ngrams(self, tagged_sent):
	'''
	Exctract ngrams, given a list of chunk rules for the previously tagged sentence.

	Keyword arguments:
	@param tagged_sent the POST tagged sentence whose ngrams need to be exctracted
	'''

        chunker = RegexpParser(CHUNK_RULE)
        tree = chunker.parse(tagged_sent)
        ngrams = []
        for item in self.__leaves(tree):
            if not item == tagged_sent:
                probable_ngram = ' '.join(self.__stemmer.stem(
                    word.lower()) for (word, pos) in item
                )
                if self.__evaluate_polarity_ngram(probable_ngram):
                    ngrams.append(probable_ngram)
        return ngrams

    def __leaves(self, tree):
	'''
	Generator for leaves in the parsed tree via the chunk rules
	
	Keyword arguments:
	@param: tree the tree whose leaves needs to be extracted.
	
	'''
        for subtree in tree.subtrees():
            yield subtree.leaves()

    def __evaluate_polarity_ngram(self, ngram):
	'''
	Filter out ngrams with no polar sense
	
	Keyword arguments:
	@param: ngram the token whose need to be evaluated as polarized or not
	
	'''

        for item in ngram.split():
            if self.__stemmer.stem(item) in self.__polar_words:
                return True
        return False

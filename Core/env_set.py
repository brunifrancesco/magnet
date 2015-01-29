import cPickle as pickle
import csv
from lxml import html
import os


from nltk.stem import SnowballStemmer

from Core.models import Status
from Core.constants import RAW_DATA_BASEPATH
from Core.constants import PICKLED_DATA_BASEPATH

mapfunc = """
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


class AbstractLoaderRetriever():
    '''Abstract class. The methods below need to be implemented
    in each class whose extends this.'''
    def raw_to_pickle(self):
        pass

    def load_from_pickle(self, join=False):
        pass


class PolarWordsEnvSetter(AbstractLoaderRetriever):
    '''Class to prepare the polar words list.'''

    def __init__(self):
        self.__raw_pos_words_path = os.path.join(
            RAW_DATA_BASEPATH, "pos_refactored.w"
        )
        self.__raw_neg_words_path = os.path.join(
            RAW_DATA_BASEPATH, "neg_refactored.w"
        )
        self.__pickled_pos_words_path = os.path.join(
            PICKLED_DATA_BASEPATH, "pos.p"
        )
        self.__pickled_neg_words_path = os.path.join(
            PICKLED_DATA_BASEPATH, "neg.p"
        )
        self.__stemmer = SnowballStemmer("english")

    def raw_to_pickle(self):
        '''Pickles raw list of polar words for further using.
        Words are stemmed before saved.
        '''

        print "Pickling raw data"
        words = list()
        with open(self._raw_pos_words_path, "rb") as input:
                for line in input.readlines():
                        words.append(self.__stemmer.stem(line.strip()))
        pickle.dump(list(set(words)), open(self.__pickled_pos_words_path, "wb"))
        words = list()
        with open(self._raw_neg_words_path, "rb") as input:
                for line in input.readlines():
                        words.append(self.__stemmer.stem(line.strip()))
        pickle.dump(list(set(words)), open(self.__pickled_neg_words_path, "wb"))
        print "Done"

    def load_from_pickle(self, join=False):
        '''Loads polar words from the pickled file.

        Keyword Arguments:
        @param: join return a joint list, or two'''

        _pos = pickle.load(
            open(os.path.join(
                PICKLED_DATA_BASEPATH, "pos.p"), "rb")
        )

        _neg = pickle.load(
            open(os.path.join(
                PICKLED_DATA_BASEPATH, "neg.p"), "rb")
        )

        if join:
            return _neg + _pos
        return _neg, _pos


class AcronymsEnvSetter(AbstractLoaderRetriever):
    '''Class to prepare the acronyms list.'''
    def __init__(self):
        self.__raw_path = os.path.join(RAW_DATA_BASEPATH, "acr_c.csv")
        self.__pickled_path = os.path.join(PICKLED_DATA_BASEPATH, "acr_c.p")

    def extract_info(self):
        '''Exctracts acronyms from a web site, using an XPATH query
        and then save it (for manual analysis) to csv file
        '''

        try:
            doc = html.parse('http://www.netlingo.com/acronyms.php')
        except Exception, e:
            print e
            exit()

        if doc:
            trs = doc.xpath("//div[@class='list_box3']//ul//li")
            for li in trs:
                try:
                    acr = li.xpath("span/a/text()")[0].encode("utf8")
                    exp = li.xpath("text()")[0].encode("utf8")
                    import csv
                    with open(self.__raw_path, 'wb') as csvfile:
                        spamwriter = csv.writer(csvfile, delimiter=',')
                        spamwriter.writerow([acr, exp])
                except Exception, e:
                    print str(e)

    def raw_to_pickle(self):
        '''Pickles raw acronyms list, lowerizing it'''

        acr_dict = {key.lower(): value.lower() for (key, value) in self.__get_acr_list()}
        pickle.dump(acr_dict, open(self.__pickled_path, "wb"))

    def __get_acr_list(self):
        '''Helper function to retrieve from the raw csv file acronyms to be pickled.'''

        result = []
        with open(self.__raw_path, 'rb') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',')
            for row in spamreader:
                try:
                    result.append((row[0], row[1]))
                except Exception, e:
                    print e
                    return result

    def load_from_pickle(self, join=False):
        '''Loads acronyms from pickled archive

        Keyword arguments:
        @param: join return one or two list, never used (False)
        '''

        return pickle.load(open(self.__pickled_path, "rb"))


class EmoticonEnvSetter(AbstractLoaderRetriever):
    def __init__(self):
        self.__raw_path = os.path.join(RAW_DATA_BASEPATH, "smileys.csv")
        self.__pickled_path = os.path.join(PICKLED_DATA_BASEPATH, "emot.p")

    def __get_emo_list(self):
        '''Helper function to retrieve raw list of emoticons'''
        result = []
        with open(self.__raw_path, 'rb') as csvfile:
                    spamreader = csv.reader(csvfile, delimiter=',')
                    for row in spamreader:
                        try:
                            result.append(row[0])
                        except Exception, e:
                            print e
                    return result

    def raw_to_pickle(self):
        '''Pickles emoticons list'''
        pickle.dump(self.__get_emo_list(), open(self.__pickled_path, "wb"))

    def load_from_pickle(self, join=False):
        '''Loads emoticons list from the pickled archive

        Keyword arguments:
        @param: join return one or two list, never used (False)
        '''
        return pickle.load(open(self.__pickled_path, "rb"))


class LargeDatasetEnvSetter:
    '''Class to load a raw set of tweets for further analysis.
    These tweets will be analyzed and features will be exctracted from them'''

    def __init__(self):
        self.__path = os.path.join(RAW_DATA_BASEPATH, "sa.csv")

    def load_tweets_in_DB(self, limit=300000):
        '''Loads tweets from raw downloaded dataset,
        storing them in the Magnet database

        Keyword arguments:
        @param: limit limit the number of storing twets
        '''

        i = 0
        print "Loading the large twitter corpus.."
        with open(self.__path, 'rb') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',')
            for row in spamreader:
                if i in range(0, limit):
                    sentiment = -3
                    if int(row[1]):
                        sentiment = 3
                    Status(
                        text=row[3].strip(),
                        sentiment=sentiment,
                        source=row[2]).save()
                    i += 1
                else:
                    return None

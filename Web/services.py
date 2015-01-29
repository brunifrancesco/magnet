from Core.classifier import ExClassifier
from Core.evaluer import RawMagnetModel
from Core.processing2 import TrainingSetAnalyzer
from Core.models import Status
from Magnet.settings import ACCESS_TOKEN_KEY
from Magnet.settings import ACCESS_TOKEN_SECRET
from Magnet.settings import CONSUMER_KEY
from Magnet.settings import CONSUMER_SECRET

from random import randint
from itertools import chain
import twitter


def get_sample_tweets():
    '''Return sample tweets retrieved by the training set,
    along with the exctracted features'''

    try:
        pos = Status.objects.filter(sentiment=3).filter(features__raw_feature_list_neg__gt=list()).skip(randint(0,2000)).limit(20)
        neg = Status.objects.filter(sentiment=-3).filter(features__raw_feature_list_neg__gt=list()).skip(randint(0,2000)).limit(20)
        ss = list(chain(pos, neg))
        return ss
    except Exception as e:
        return e


def classify(text, twitter_query=False):
    '''Classify a text or search on Twitter text to be classified

    Keywords arguments:
    @param: text A plain text or a twitter query
    @param: twitter_query if True,
        states that the text is a Twitter query search term
    '''
    try:
        if not twitter_query and TrainingSetAnalyzer().is_objective(text):
            return [dict(label="Objective", text=text)]
        model = RawMagnetModel()
        ex_classifier = ExClassifier(model=model)
        if twitter_query:
            return search_and_classify(text, ex_classifier)
        result = ex_classifier.classify_bulk([text])
        return result
    except Exception as e:
        print e
        return None


def search_and_classify(text, classifier):
    '''Return classified text, searched on twitter, given the text query term
    Keyword arguments:
    @param: text the text to be looked for
    @param: classifier the NB classifier instance
    '''
    api = twitter.Api(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)
    results = api.GetSearch(term=text, geocode=None, since_id=None, max_id=None, until=None, count=100, lang='en', locale=None, result_type='mixed', include_entities=None)
    return classifier.classify_bulk(result.text for result in results)

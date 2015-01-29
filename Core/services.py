from Core.models import Status
from Core.models import MagnetModel


def get_tweets_for_filtering_ngrams(skip):
    '''
    Retrieve tweets from raw training set
    to be apply the filtering unigrams-ngrams

    Keyword arguments:
    @param: skip elements to skip in retrieving tweets
    '''

    return Status \
        .objects \
        .filter(features__raw_feature_list_neg__gt=[]) \
        .filter(features__ngrams__gt=[]) \
        .skip(skip*5000) \
        .limit(5000) \



def get_tweets_for_analyzing(skip):
    '''
    Retrieve tweets for being analyzed

    Keyword arguments:
    @param: skip elements to skip in retrieving tweets
    '''
    return Status \
        .objects \
        .filter(features__exists=False) \
        .filter(sentiment__ne=0)\
        .skip(skip*5000) \
        .limit(5000)


def get_tweets_for_pruning():
    '''
    Retrieve tweets for being pruned

    Keyword arguments:
    @param: skip elements to skip in retrieving tweets
    '''
    return Status \
        .objects \
        .filter(features__raw_feature_list_neg__gt=[])


def get_magnet_models():
    '''
    Retrieve all magnet models from database

    Keyword arguments:
    @param: skip elements to skip in retrieving tweets
    '''
    return MagnetModel.objects

from mongoengine import *


class Features(EmbeddedDocument):
    '''Map the Features (embedded in Status) document at application level'''

    filtered_unigram = ListField(StringField())
    raw_feature_list_neg = ListField(StringField())
    emoticons = ListField(StringField())
    ngrams = ListField(StringField())


class Status(Document):
    '''Map the Status embedded document at application level'''

    text = StringField(required=True)
    sentiment = IntField(required=False, default=-2)
    word = StringField(required=False)
    source = StringField(required=False)
    features = EmbeddedDocumentField(Features)

    def set_features(
        self,
        raw_feature_list_neg,
        emoticons,
        ngrams
    ):
        '''
        Save features for the given Status document

        Keyword Arguments:
        @param: raw_feature_list_neg unigrams lists
        @param: emoticons emoticons lists
        @param: ngrams ngrams list
        '''

        if raw_feature_list_neg or emoticons or ngrams:
                self.features = Features(
                    raw_feature_list_neg=raw_feature_list_neg,
                    emoticons=emoticons,
                    ngrams=ngrams)
        else:
            self.sentiment = 0
        self.save()


class Perfomance(EmbeddedDocument):
    '''Map the Perfomance (embedded in MagnetModel) document at application level'''

    tweet_set_size = IntField(required=True)
    accuracy = FloatField(required=True)
    prec_pos = FloatField(required=True)
    prec_neg = FloatField(required=True)
    rec_pos = FloatField(required=True)
    rec_neg = FloatField(required=True)
    fmeas_pos = FloatField(required=True)
    fmeas_neg = FloatField(required=True)


class MagnetModel(Document):
    '''Map the Status embedded document at application level'''

    _type = IntField(required=True)
    performances = ListField(EmbeddedDocumentField(Perfomance))
    features_list = ListField(StringField(required=True))

    def set_details(self, typee, model, performances):
        '''Set classifier score for the specific MagnetModel'''

        self._type = typee
        self.features_list = model.features_list
        for performance in performances:
            self.performances.append(Perfomance(**performance))
        print "saving model..."
        self.save()

from Core.models import MagnetModel
from Core.exceptions import MagnetException
from Core.classifier import ExClassifier
from Core.services import get_magnet_models

import pygal


class RawMagnetModel:
    '''Meta models used in the classification process'''
    def __init__(self, limit=80000, features_list=["UNNN", "NGR", "EMOT"]):
        if "UNNN" in features_list and "UNNN_F" in features_list:
            raise MagnetException("Filtered unigrams and raw unigrams cannot be used in the same model")
        self.limit = limit
        self.features_list = features_list

    def __str__(self):
            '''String representation of the RawMagnetModel'''
            s = '''
            ------>[START MODEL SPECS]<------
            Limit: %i
            Features list: %s
            ------>[END MODEL SPECS]<------
            ''' % (self.limit, self.features_list)
            return s


def build_magnet_models_for_evaluation():
    '''
    Helper function to build future prepare MagnetModels which will
    be stored in the database
    '''

    models = {i: [] for i in range(1, 9)}

    for limit in range(5000, 105000, 5000):
        models[1].append(RawMagnetModel(
            limit=limit,
            features_list=["UNNN", "NGR", "EMOT"])
        )

        models[4].append(RawMagnetModel(
            limit=limit,
            features_list=["UNNN", "EMOT"])
        )

        models[5].append(RawMagnetModel(
            limit=limit,
            features_list=["UNNN_F", "NGR", "EMOT"])
        )

        models[6].append(RawMagnetModel(
            limit=limit,
            features_list=["UNNN_F"])
        )

        models[8].append(RawMagnetModel(
            limit=limit,
            features_list=["NGR"])
        )

    return models


def turn_raw_in_db_models():
    '''Set performances to MagnetModels instances and save them'''

    for _type, models in build_magnet_models_for_evaluation().iteritems():
        scores = []
        for model in models:
            try:
                ex = ExClassifier(model)
                performances = ex.evaluate_precision_recall_f_measure()
                performances["accuracy"] = ex.evaluate_accuracy()
                performances["tweet_set_size"] = model.limit
                scores.append(performances)
            except MagnetException as me:
                print "Error in evaluating accuracy: %s" % str(me)
            except Exception as ee:
                print "Error in evaluating performances: %s" % str(ee)
        try:
            mm = MagnetModel()
            mm.set_details(_type, model, scores)
        except Exception as ee:
            print ee


def compute_graphs_accuracy():
    '''Compute classifier scores charts'''
    models = get_magnet_models()
    bar_chart = pygal.Bar(x_label_rotation=20, print_values=False, range=(.5, .75))
    bar_chart.title = 'Accuracies (in %)'
    ts = [p.tweet_set_size for p in models[0].performances]
    bar_chart.x_labels = map(str, ts)
    bar_chart.add('1', [p.accuracy for p in models[0].performances])
    bar_chart.add('2', [p.accuracy for p in models[1].performances])
    bar_chart.add('3', [p.accuracy for p in models[2].performances])
    bar_chart.add('4', [p.accuracy for p in models[3].performances])
    bar_chart.add('5', [p.accuracy for p in models[4].performances])
    bar_chart.render_to_file("accuracies.svg")

    bar_chart = pygal.Bar(x_label_rotation=20, print_values=False)
    bar_chart.title = 'F1 Measure for positive tweets (in %)'
    ts = [p.tweet_set_size for p in models[0].performances]
    bar_chart.x_labels = map(str, ts)
    bar_chart.add('1', [p.fmeas_pos for p in models[0].performances])
    bar_chart.add('2', [p.fmeas_pos for p in models[1].performances])
    bar_chart.add('3', [p.fmeas_pos for p in models[2].performances])
    bar_chart.add('4', [p.fmeas_pos for p in models[3].performances])
    bar_chart.add('5', [p.fmeas_pos for p in models[4].performances])
    bar_chart.render_to_file("fmeas_pos.svg")

    bar_chart = pygal.Bar(x_label_rotation=20, print_values=False, range=(.5, .75))
    bar_chart.title = 'F1 Measure for negative tweets (in %)'
    ts = [p.tweet_set_size for p in models[0].performances]
    bar_chart.x_labels = map(str, ts)
    bar_chart.add('1', [p.fmeas_neg for p in models[0].performances])
    bar_chart.add('2', [p.fmeas_neg for p in models[1].performances])
    bar_chart.add('3', [p.fmeas_neg for p in models[2].performances])
    bar_chart.add('4', [p.fmeas_neg for p in models[3].performances])
    bar_chart.add('5', [p.fmeas_neg for p in models[4].performances])
    bar_chart.render_to_file("fmeas_neg.svg")

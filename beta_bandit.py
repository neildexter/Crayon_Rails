# Shamelessly ripped from https://gist.github.com/stucchio/5383015#file-beta_bandit_test-py

import numpy as np
import operator as op


class BetaBandit(object):
    def __init__(self, all_keys):
        self.trials = {key: 0 for key in all_keys}
        self.all_keys = all_keys
        self.mean = {key: 0 for key in all_keys}

    def set_results(self, key, value):
        #print successes, trials
        self.trials[key] += 1
        if self.trials[key] == 1:
            self.mean[key] = value
        else:
            self.mean[key] = ((self.trials[key]-1)*self.mean[key]+value)/self.trials[key]

    def get_recommendation(self):
        sampled_theta = {}
        for key in self.all_keys:
            sampled_theta[key] = np.random.normal(self.mean[key], 20)
        # Return the index of the sample with the largest value
        return max(sampled_theta.iteritems(), key = op.itemgetter(1))[0]
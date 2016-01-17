from __future__ import print_function, division, absolute_import
from .lstd import LSTDLearner
from ..testutil import MockPolicy, MockPolicyFeatureModule

import unittest
import scipy
from numpy.testing import assert_array_almost_equal, assert_almost_equal

from pybrain.datasets import ReinforcementDataSet
from librl.policies.boltzmann import BoltzmanPolicy

class TDLearnerTestCase(unittest.TestCase):
    def setUp(self):
        self.policy = MockPolicy({}, [0, 0])
        self.module = MockPolicyFeatureModule(self.policy)
        self.tracestepsize = 0.9
        self.actorstepsize = 3
        self.maxcriticnorm = 1
        self.learner = LSTDLearner(self.policy, self.tracestepsize,
                                   self.actorstepsize, self.maxcriticnorm,
                                   self.module)

    def testCritic(self):
        assert_array_almost_equal([[1, 0], [0, 1]], self.learner.A)
        assert_array_almost_equal([0, 0], self.learner.b)

        self.learner.A = scipy.array([[2, 0],
                                      [0, 4]], dtype=float)
        self.learner.b = scipy.array([2, 3], dtype=float)
        self.learner.z = scipy.array([-1, 1], dtype=float)
        self.learner.k = 1
        self.learner.critic(1, scipy.array([1, 2]), 2, scipy.array([4, 3]))
        # r = -inv(A) * b
        assert_array_almost_equal([-1, -0.75], self.learner.r)
        # featureDifference = [3, 1], gamma = 0.5
        # A += 0.5 * ( [-1] * [3, 1] - [[2, 0] )
        #              [ 1]             [0, 4]]
        assert_array_almost_equal(0.5, self.learner.gamma)
        assert_array_almost_equal([[-0.5, -0.5],
                                   [1.5, 2.5]], self.learner.A)

from __future__ import print_function, division, absolute_import

class MockPolicyFeatureModule(object):
    def __init__(self, policy):
        self.policy = policy
        self.outdim = len(self.policy.theta)

    def get_theta(self): return self.policy.theta
    def set_theta(self, val): self.policy.theta = val
    theta = property(fget = get_theta, fset = set_theta)

    def decodeFeature(self, feature, name):
        el = self.outdim * self.outdim + self.outdim
        assert len(feature) == el, 'invalid feature for MockPolicyFeatureModule'
        if name == 'first_order':
            return feature[:self.outdim]
        else:
            return feature[self.outdim:].reshape((self.outdim, self.outdim))

class MockLearner(object):
    def __init__(self, policy):
        self.module = MockPolicyFeatureModule(policy)

class MockPolicy(object):
    def __init__(self, data, theta=None):
        self.data = data
        if theta is None:
            self.theta = [0, 0]
        else:
            self.theta = theta

    def activate(self, obs):
        return self.data[obs]

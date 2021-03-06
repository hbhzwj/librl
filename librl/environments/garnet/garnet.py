from __future__ import print_function, division, absolute_import
import scipy
from pybrain.rl.environments.environment import Environment
from pybrain.rl.environments.task import Task
from librl.util import zdump, zload

# FIXME(hbhzwj) add unittest for GarnetTask and GarnetEnvironment.
class GarnetTask(Task):
    """Garnet Task

    The expected reward for each transition is a normally distributed random
    variable with mean 0 and unit variance. The actual reward id selected
    randomly according to a normal distribution with mean equal to the
    expected reward and standard deviation \sigma.

    The state-action observation is created based on pg. 29 of
    Bhatnagar, Shalabh, et al. "Natural actor-critic algorithms." Automatica
    45.11 (2009): 2471-2482.
    phi(x, u) = (0...0, fs, 0...0)
                  u-1        m-i
    """
    def __init__(self, environment, sigma):
        super(GarnetTask, self).__init__(environment)
        self.sigma = sigma
        self.rewardCache = dict()
        self.numStates = self.env.numStates
        self.numActions = self.env.numActions

    def _getExpectedReward(self, key):
        expectedReward = self.rewardCache.get(key)
        if expectedReward is not None:
            return expectedReward
        self.rewardCache[key] = scipy.random.randn()
        return self.rewardCache[key]

    def performAction(self, action):
        self.env.lastAction = action
        super(GarnetTask, self).performAction(action)

    def getReward(self):
        key = (self.env.prevState, self.env.curState,
               int(self.env.lastAction[0]))
        expectedReward = self._getExpectedReward(key)
        reward = self.sigma * scipy.random.randn() + expectedReward
        return reward

    @property
    def outdim(self):
        edim = self.env.outdim
        return self.numActions * edim * self.numActions

    def getObservation(self):
        sensors = self.env.getSensors()
        fd = len(sensors)
        feature = scipy.zeros((self.numActions, fd * self.numActions))
        for i in xrange(self.numActions):
            feature[i, (i*fd):((i+1)*fd)] = sensors
        return feature.reshape(-1)

class GarnetLookForwardTask(GarnetTask):
    """Garnet task whose feature is created by looking forward.

    This class is a garnet task with a new feature. The state-action feature is
    the expected state feature value given this action.
    phi(x, u) = E(fs|u) - fs
    """
    @property
    def outdim(self):
        edim = self.env.outdim
        return self.numActions * edim

    def getObservation(self):
        sensors = self.env.getSensors()
        fd = len(sensors)
        feature = scipy.zeros((self.numActions, fd))
        for i in xrange(self.numActions):
            nextStates = self.env.transitionStates[i, self.env.curState, :]
            prob = self.env.transitionProb[i, self.env.curState, :]
            res = scipy.zeros((fd,))
            for ss, p in zip(nextStates, prob):
                obs = self.env.getSensors(int(ss))
                res += scipy.array(obs)* p
            feature[i, :] = res - scipy.array(sensors)
        return feature.reshape(-1)

# TODO(hbhzwj): replace it with StateObsWrapperTask
class GarnetLookForwardWithStateObsTask(GarnetTask):
    """Garnet task with both looking forward feature ans state feature"""
    @property
    def outdim(self):
        edim = self.env.outdim
        return (self.numActions + 1) * edim

    def getObservation(self):
        sensors = self.env.getSensors()
        fd = len(sensors)
        feature = scipy.zeros((self.numActions + 1, fd))
        for i in xrange(self.numActions):
            nextStates = self.env.transitionStates[i, self.env.curState, :]
            prob = self.env.transitionProb[i, self.env.curState, :]
            res = scipy.zeros((fd,))
            for ss, p in zip(nextStates, prob):
                obs = self.env.getSensors(int(ss))
                res += scipy.array(obs)* p
            feature[i, :] = res - scipy.array(sensors)
        feature[self.numActions, :] = scipy.array(sensors)

        return feature.reshape(-1)


class GarnetEnvironment(Environment):
    """Generic Average Reward Non-stationary Environment TestBed

    Parameters
    -----
    numStates : int
        # of states.
    numActions : int
        # of actions
    branching : int
        # of possible next states for each state-action pair.
    feaDim, feaSum: int
        the feature for each state is a vector of {0, 1} whose length is feaDim
        and whose sum is feaSum.

    """
    initState = 0
    def __init__(self, numStates, numActions, branching, feaDim, feaSum,
                 savePath=None, loadPath=None):
        self.numStates = numStates
        self.numActions = numActions
        self.branching = branching
        self.feaDim = feaDim
        self.feaSum = feaSum

        if loadPath is not None:
            self._load(loadPath)
        else:
            self._genTransitionTable()
            self._genStateObs()

        if savePath is not None:
            self._save(savePath)

        self.curState = self.initState
        # null value for action
        self.lastAction = scipy.array([-1])

    @property
    def outdim(self):
        return self.feaDim

    def _save(self, savePath):
        message = dict()
        message['transitionStates'] = self.transitionStates
        message['transitionProb'] = self.transitionProb
        message['stateObs'] = self.stateObs
        zdump(message, savePath)

    def _load(self, loadPath):
        message = zload(loadPath)
        self.transitionStates = message['transitionStates']
        self.transitionProb = message['transitionProb']
        self.stateObs = message['stateObs']

    def _genStateObs(self):
        pos = range(self.feaDim)
        stateObs = set()
        while len(stateObs) < self.numStates:
            obs = scipy.zeros((self.feaDim,), dtype=int)
            ones = scipy.random.choice(pos, self.feaSum, False)
            obs[ones] = 1
            stateObs.add(tuple(obs.tolist()))
        self.stateObs = list(stateObs)

    def _genTransitionTable(self):
        # generate state that will be transited to and corresponding
        # probabilities.
        self.transitionStates = scipy.zeros((self.numActions, self.numStates, self.branching))
        self.transitionProb = scipy.zeros((self.numActions, self.numStates, self.branching))
        allStates = scipy.arange(self.numStates)
        for u in xrange(self.numActions):
            for i in xrange(self.numStates):
                self.transitionStates[u, i, :] = scipy.random.choice(allStates,
                                                                     size=self.branching,
                                                                     replace=False)
                # probabilities
                cutPoints = scipy.random.rand(self.branching-1)
                cutPoints = sorted(cutPoints.tolist() + [0, 1])
                self.transitionProb[u, i, :] = scipy.diff(cutPoints)

    def getSensors(self, state=None):
        if state is None:
            state = self.curState
        return self.stateObs[state]

    def performAction(self, action):
        action = action[0]
        states = self.transitionStates[action, self.curState, :]
        prob = self.transitionProb[action, self.curState, :]
        nextState = scipy.random.choice(states, size=1, p=prob)
        nextState = int(nextState[0])
        self.prevState = self.curState
        self.curState = nextState

    def reset(self):
        self.curState = self.initState

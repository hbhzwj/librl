import scipy
import types
from pybrain.rl.environments.mazes import Maze

def cityBlockDistance(x, y):
    return abs(x[0] - y[0]) + abs(x[1] - y[1])

class TrapMaze(Maze):
    """The difference between TrapMaze and Maze is that
    - in mazeTable, 1 means wall, -1 means trap.
    - when robot reaches a Wall(unsafeState), it will start over,
    - The robot is not fully controllable, it is a markov chain and described
      by transition probability.
    - the order of action is [N, E, S, W]
    """
    # directions
    N = (-1, 0)
    S = (1, 0)
    E = (0, 1)
    W = (0, -1)

    WALL_FLAG = 1
    TRAP_FLAG = -1
    GOAL_FLAG = 2
    def __init__(self, topology, startPos, tranProb, **args):
        assert(type(startPos) == types.TupleType)
        self.perseus = self.startPos = startPos
        self.initPos = [startPos]
        self.tranProb = tranProb
        if (type(topology) == types.ListType):
            topology = scipy.array(topology)
        self.mazeSize = topology.shape
        self.mazeTable = topology
        self.setArgs(**args)
        self.bang = False
        self.allActions = [self.N, self.E, self.S, self.W]
        self.numActions = len(self.allActions)

        # find goal states from env mask.
        self.goalStates = []
        for i in xrange(self.mazeSize[0]):
            for j in xrange(self.mazeSize[1]):
                if self.isGoal((i, j)):
                    self.goalStates.append((i, j))


        self.cacheMinDistanceToGoal = {}

    @property
    def outdim(self):
        return self.feaDim

    def isTrap(self, pos):
        return self.mazeTable[pos[0], pos[1]] == self.TRAP_FLAG

    def isWall(self, pos):
        return self.mazeTable[pos[0], pos[1]] == self.WALL_FLAG

    def isGoal(self, pos):
        return self.mazeTable[pos[0], pos[1]] == self.GOAL_FLAG

    def isOutBound(self, pos):
        return True if ( pos[0] >= self.mazeSize[0] or pos[1] >= self.mazeSize[1] or pos[0] < 0 or pos[1] < 0) else False

    def performAction(self, action):
        """TrapMaze is stochastic. When the control is E, the robot doen't necessarily
        goto the east direction, instead there is some transition probability to W, N, S, too.
        if the next position is out of the scene, the robot will not move. If the next position
        is a trap, the robot to go back to starting position and the self.bang flag is set."""
        # if the current state is a trap, move to startPos regardless of the
        # action.
        if self.isTrap(self.perseus):
            self.perseus = self.startPos
            return

        assert action >= 0 and action < self.numActions
        actions = range(self.numActions)
        realActionIndex = scipy.random.choice(actions,
                                              p=self.tranProb[action])
        realAction = self.allActions[realActionIndex]
        nextPos = self._moveInDir(self.perseus, realAction)

        # If outside or reach wall, don't move and set bang as true
        if self.isOutBound(nextPos) or self.isWall(nextPos):
            # position (perseus) is not changed.
            self.bang = True
            return

        self.perseus = nextPos
        self.bang = False

    def reset(self):
        self.bang = False
        self.perseus = self.startPos

    def getSensors(self, state=None):
        if state is None:
            state = self.perseus

        safetyScore = 1.0 - self.isTrap(state)
        return scipy.array([safetyScore,
                            -1.0 * self.getMinDistanceToGoal(state)])

    @property
    def outdim(self):
        return 2

    def getMinDistanceToGoal(self, state):
        """Get the minimium distance to any of goal stats."""
        searchKey = tuple(state)
        cacheValue = self.cacheMinDistanceToGoal.get(searchKey)
        if cacheValue: return cacheValue

        distance = float('inf')
        for goal in self.goalStates:
            tmp = cityBlockDistance(goal, state)
            if tmp < distance:
                distance = tmp

        self.cacheMinDistanceToGoal[searchKey] = distance
        return distance

#!/usr/bin/env python

MAX_VAL = None
# MAX_VAL = 800
def loadtxt(fname):
    fid = open(fname)
    value = []
    while True:
        line = fid.readline()
        if not line: break
        if line[0] == '#':
            kl = line.rsplit(' ')
            keys = [k.strip('#\n') for k in kl]
            continue
        val = line.rsplit(' ')
        value.append([float(v) for v in val])
    return keys, value

def loadTheta(fname):
    # fid = open('./res/lstdac_theta.tr')
    fid = open(fname)
    theta = []
    while True:
        line = fid.readline()
        if not line: break
        if line[0] == '#': continue
        val = line.rsplit(' ')
        theta.append([float(v) for v in val])
    return theta

from matplotlib.pyplot import *
from numpy import divide, cumsum
def plotRP(fname, ptNum, showFlag=True, smoothFlag=False, marker=None):
    keys, values = loadtxt(fname)
    print 'keys, ', keys
    col_values = zip(*values)
    print 'len col_values, ', len(col_values)

    # theta0 = col_values[keys.index('theta0')]
    # theta1 = col_values[keys.index('theta1')]
    reward = col_values[keys.index('reward')]
    it = col_values[keys.index('it')]

    # n = len(theta0)
    n = len(reward)
    if MAX_VAL: n = int(MAX_VAL)
    stepSize = int(n / ptNum) if ptNum else 1
    trace = dict(reward=[], time=[], it=[])
    for i in xrange(0, n, stepSize):
        trace['reward'].append(reward)
        # trace['time'].append(time)
        trace['it'].append(it[i])
    X = trace['it']
    if not smoothFlag:
        Y = trace['reward']
    else:
        rp = trace['reward']
        cum_rp = cumsum(rp)
        smooth_rp = [cum_rp[i] * 1.0/ (i+1) for i in xrange(len(rp))]
        Y = smooth_rp

    if marker:
        plot(X, Y, marker)
    else:
        plot(X, Y)

    if showFlag: show()

if __name__ == "__main__":
    # plotRP('./enac.tr', 50)
    # plotRP('./hac.tr', 50, False)
    # plotRP('./lstdac.tr', 50, False)
    # plotRP('./tdac.tr', 50, False)

    # plotRP('./enac.tr', 200)
    # plotRP('./hac.tr', None, False)
    # plotRP('./hac.tr', 200, False)
    # plotRP('./lstdac.tr', 200, False)
    # plotRP('./res/hac_good.tr', 200, False)
    # plotRP('./res/lstdac.tr', 200, False)
    # plotRP('./tdac.tr', 200, False)
    # plotRP('./tdac.tr', 200, False, True)
    # plotRP('./tdac.tr', 500, False, True)

    # plotRP('./enac.tr', None, False)
    # plotRP('./enac.tr', 100, False)
    # plotRP('./hac.tr', 200, False)
    # plotRP('./lstdac.tr', 200, False)
    # plotRP('./lstdac.tr', 100, False)
    # plotRP('./lstdac.tr', 100, False, True)
    # plotRP('./lstdac.tr', 500, False, True)
    # plotRP('./tdac_back.tr', 200, False)

    # plotRP('./nac.tr', 50, False)
    # plotRP('./nac.tr', 200, False)
    # plotRP('./enac.tr', None, False)
    # plotRP('./enac.tr', None, False, True)

    # plotRP('./res_good/enac.tr', 200, False)
    # plotRP('./res_good/hac.tr', 200, False)
    # plotRP('./res_good/lstdac.tr', 200, False)
    # plotRP('./res_good/tdac.tr', 200, False)
    # show()
    # plotRP('./res/lstdac_theta.tr', 50, False)
    # plotRP('./res/tdac_theta.tr', 50, False)
    # plotRP('./res/enac_theta.tr', 50, False)
    # legend(['lstdac', 'tdac'])
    # legend(['hac','lstdac', 'tdac'])
    # legend(['hac','lstdac'])
    # legend(['enac','hdac', 'lstdac', 'tdac'])
    # legend(['tdac','lstdac', 'enac'])

    # plotRP('./hac.tr', 200, False, True, '-')
    # plotRP('./hac.tr', None, False, True, '-')
    # plotRP('./hac.tr', 50, False, True, '-')
    plotRP('./hac.tr', 50, False, False, '-')
    # plotRP('./tdac.tr', 200, False, True)

    # plotRP('./enac.tr', None, False, True, '--')
    # plotRP('./lstdac.tr', None, False, True, '-.')
    # plotRP('./lstdac.tr', 200, False, True, '-.')


    xlabel('iteration number')
    ylabel('reachability probability')
    # legend(['hac','tdac', 'enac', 'lstdac'])
    legend(['hac','enac', 'lstdac'])
    savefig('comparison_es.eps')
    # show()

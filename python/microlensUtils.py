#
# microlensUtils.py
#

# methods to convert from sims_maf predictions to the N_RC and N_\ast
# of Poleski 2016, to produce the "sensitivity" from these, and to
# return the gamma value.

# WIC 2016-05-24

import numpy as np

### (Could make this an object but it's not clear that would gain us
### much...)

# "Wrapper" method
def gammaFromMetricValues(nLSST=np.array([]), nBri=np.array([]) ):

    """Wrapper routine that returns the P16-predicted microlensing
    rate from sims_maf output N(I < 27.5) and N(I < 20.5)
    respectively."""

    nRC  = densRCG(nLSST)
    nSrc = densSrc(nBri)
    sens = sensitivity(nRC, nSrc)
    gamma = gammaFromSens(sens)

    return gamma


def densRCG(nLSST=np.array([]), scale=50.88, const=0.):

    """Returns tne N_RCG in P16 given the LSST density. Default
    parameters return P16's N_RCG in units of thousands per square
    degree, with input sims_maf stars per square arcsec"""

    return nLSST * scale + const

def densSrc(nBri=np.array([]), scale=1.5, const=2.12, needsConv=True):

    """Returns the N_{\ast}(I < 20.5) of Poleski 2016 with sims_maf's
    predicted N_{\ast}(I < 20.5)."""

    # UPDATE: when I originally wrote this, it used the converted
    # density (in millions per square degrees). Set that here.
    nUse = np.copy(nBri)
    if needsConv:
        nUse = nBri * 3600.0**2 / 1.0e6

    return nUse * scale + const

def sensitivity(nRC=np.array([]), nSrc = np.array([]), \
                    alpha=0.55):

    """Returns P16's S value given N_RC and N_ast"""

    return nRC**alpha * nSrc

def gammaFromSens(x, parsPow=[19.13, -24.99], \
                      parsLine=[0.767, -14.6], \
                      hiLim=20., loLim=12.):
    
    """Returns Poleski 2016 gamma given the sensitivity"""
    
    bHi = x >= hiLim
    bLo = x < loLim
    bMed = (~bHi) & (~bLo)
    
    yRet = np.zeros(np.size(x))
    yRet[bHi]  = parsLine[0] * x[bHi] + parsLine[1]
    yRet[bMed] = 10.0**parsPow[1] * x[bMed]**parsPow[0]
    yRet[bLo] = np.min(yRet[bMed]) # enforce smoothness
    
    return yRet

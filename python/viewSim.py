#
# viewSim.py
#

#
# WIC 2016-09-08
#

# Quick routines to view a simulation set in prep for an LSST metric

# Loading the >300M ascii file with astropy brings my laptop to a
# halt. 

import os, time
import numpy as np
from astropy.table import Table, Column
from astropy.io import fits

from scipy.optimize import leastsq # simple least-squares for the moment

import matplotlib.pylab as plt

class ConvertAscii(object):

    """Read the simulation samples and compute a few simple things"""

    def __init__(self, pathSim='', \
                     rowsChunk=100000, \
                     Verbose=True):

        # Source for the simulation
        self.pathSim = pathSim[:]
        if len(self.pathSim) < 1:
            self.pathSim='/Users/clarkson/Data/LSST/victorsModels/UCLAN_2016-09-07/12M_hr_diff_coeff0.05.01000.stars.asc'

        # Path for final binary catalog
        self.pathBinary = 'DUM.fits'
        self.setPathBinary()

        # Numpy array for the full set of (floating point) data
        self.aSim = np.array([])
        self.nLines = 0

        # Set the columns for ascii and units for metadata
        self.setColumnsAndUnits()

        # Some internal variables
        self.DMeta = {}

        # Filename for intermediate fits file
        self.filFits = 'TEST.fits'

        # Control variables
        self.rowsChunk=rowsChunk
        self.Verbose=Verbose

    def setPathBinary(self):

        """Sets the filename for the output binary file"""

        if len(self.pathSim) < 1:
            return

        sStem = self.pathSim.split('/')[-1].split('.asc')[0]
        self.pathBinary='%s.fits' % (sStem)

    def setColumnsAndUnits(self):

        """Sets the columns for the input ascii dataset"""

        self.cols = ['X', 'Y', 'Z', 'vX', 'vY', 'vZ', 'Mass', 'Age', 'FeH', 'alphaFe']
        
        # Set the units. Currently this is for humans to read...
        self.units = {}
        for sCoo in ['X', 'Y', 'Z']:
            self.units['%s'  % (sCoo)] = 'kpc'  # positions
            self.units['v%s' % (sCoo)] = 'km/s' # velocities

        self.units['Age'] = 'Gyr'
        self.units['Mass'] = '2.33e5 MSun'
        self.units['FeH'] = 'dex'
        self.units['alphaFe'] = 'dex'

    def loadSim(self):

        if not os.access(self.pathSim, os.R_OK):
            if self.Verbose:
                print "ConvertAscii.loadSim WARN - cannot read input path %s" \
                    % (self.pathSim)
            return

        self.setChunkBoundaries()
        t0 = time.time()
        for iChunk in range(len(self.chunksLo)):
            self.getSimSection(iChunk)

            if self.Verbose:
                print "Chunk %3i:" % (iChunk), \
                    np.shape(self.aSim), '%.2e' % (time.time()-t0)

#        TOO SLOW        
#        if self.Verbose:
#            print "ConvertAscii.loadSim INFO - importing ascii file..."
#            t0 = time.time()
#        self.tSim=Table.read(self.pathSim, data_start=2, format='ascii')
        
#        if self.Verbose:
#            t1 = time.time()
#            print "ConvertAscii.loadSimINFO - ... done after %.1f seconds" \
#                % (t1 - t0)

    def countLines(self):

        """useful to learn the number of lines in the file"""

        # Apparently python is using C under the hood just like wc, so
        # this should not be hugely slow... let's check... 
        # 
        # Actually for this file the routine below is FASTER than wc
        # (takes about half a second on a 2 million line file).

        self.nlines = 0
        if not os.access(self.pathSim, os.R_OK):
            if self.Verbose:
                print "SimSample.countLines FATAL - cannot read path %s" \
                    % (self.pathSim)
            return

        with open(self.pathSim, 'r') as wObj:
            for sLine in wObj:
                self.nLines = self.nLines + 1

    def setChunkBoundaries(self):

        """Sets up an array of chunk lower boundaries for reading in later"""

        # We set up exactly the quantities we'll need later: first row
        # number and the number of rows in each chunk

        if self.nLines < 1:
            self.countLines()
        self.chunksLo = np.arange(0., self.nLines, self.rowsChunk)
        self.chunksLo[0] = 1.

        self.chunksN = np.roll(self.chunksLo, -1) - self.chunksLo
        self.chunksN[-1] = self.nLines - self.chunksLo[-1]

        self.chunksLo = np.asarray(self.chunksLo, 'int')
        self.chunksN = np.asarray(self.chunksN, 'int')

    def getSimSection(self, iChunk=0):

        """Reads in a section of the simulation file"""

        # Do nothing if being asked to read in improper entry
        if iChunk >= np.size(self.chunksN):
            return

        aChunk = np.genfromtxt(self.pathSim, \
                                   skip_header=self.chunksLo[iChunk], \
                                   max_rows=self.chunksN[iChunk])

        # Rather than mess with indices in the final array, let's just
        # try hstack. We can optimize later if it turns out to be
        # necessary.
        if np.size(self.aSim) < 1:
            self.aSim = np.copy(aChunk)
            return

        self.aSim = np.vstack(( self.aSim, aChunk ))

    def dumpToFits(self):

        """Dumps the numpy array to fits for quicker reading"""

        if np.size(self.aSim) < 1:
            return

        fits.writeto(self.filFits, self.aSim, clobber=True)

    def loadFromFits(self):

        """Reads the array from fits"""

        self.aSim = fits.getdata(self.filFits)
        self.nLines = np.shape(self.aSim)[0]

    def simToTable(self):

        """Converts the simulation to an astropy table for convenient
        writing, storing of metadata, etc."""

        if np.size(self.aSim) < 1:
            return

        tSim = Table()
        for iCol in range(np.shape(self.aSim)[-1]):
            colName = self.cols[iCol]
            colUnit = self.units[colName]
            colVals = self.aSim[:,iCol]

            # Generate this column
            tSim[colName] = Column(colVals, unit=colUnit)

        # write THIS to fits - should include the metadata now.
        tSim.write(self.pathBinary, overwrite=True)

class SimSamples(object):

    """Imports the simulation, computing a few useful quantities along
    the way"""

    # The simulation is typically small enough to fit comfortably into
    # RAM, so we don't need to do anything clever here.

    def __init__(self, simPath='', \
                     nStripsFeH=20, minFeH=-1.0, maxFeH=0.15, \
                     RMin = 7., RMax= 9., \
                     ZMin = 0.5, ZMax = 1., \
                     AgeMin=0., AgeMax=15.):

        self.simPath=simPath[:]
        if len(self.simPath) < 1:
            self.simPath='/Users/clarkson/Data/LSST/victorsModels/UCLAN_2016-09-07/12M_hr_diff_coeff0.05.01000.stars.fits'

        # Let's go with a table for the moment
        self.tSim = Table()

        # selected objects
        self.bGood = np.array([])
        self.bSel = np.array([])

        # selection criteria
        self.RMin = RMin
        self.RMax = RMax
        self.ZMin = ZMin
        self.ZMax = ZMax 
        self.AgeMin = AgeMin
        self.AgeMax = AgeMax

        # number of strips in Fe/H to use
        self.nStripsFeH = nStripsFeH
        self.minFeH = minFeH
        self.maxFeH = maxFeH
        self.stripsFeH = np.array([])

        # declare the statistics we want now
        self.stripFeHs = np.array([])
        self.stripCounts = np.array([])
        self.stripMeans = np.array([])
        self.strimMedns = np.array([])
        self.stripStdds = np.array([])

        # set of fitted parameters for the unbroken and broken
        # straight line
        self.parsBroken = np.array([])
        self.parsSingle = np.array([])
        self.successBroken = np.array([])
        self.successStraight = np.array([])

        self.chisqStraight = 0.
        self.chisqBroken = 0.

        # For first-order, let's just try a flat error
        self.uncPM = 0.2 # mas/yr, be optimistic
        self.useFlatUncertainty = True

        # Data - solar galactocentric radius 
        self.RSol = 8.0  # kpc

        # self.WSol = 240. # km/s, sun's transverse velocity, not
        # needed right now

    def loadFitsSim(self):

        """Loads the fits simulation."""

        if not os.access(self.simPath, os.R_OK):
            return

        # Since reading the ascii version takes a very long time and
        # gums up the system, don't load if not fits...
        if self.simPath.split('.')[-1].find('fits') < 0:
            print "SimSamples.loadFitsSim WARN - doesn't seem to be a fits file."
            return

        self.tSim = Table.read(self.simPath)

        self.bGood = np.isfinite(self.tSim['X'])

    def calcVphi(self):

        """Calculates the vPhi column"""

        if len(self.tSim) < 1:
            return

        self.tSim['R'] = Column( np.sqrt(self.tSim['X']**2 + \
                                             self.tSim['Y']**2 + \
                                             self.tSim['Z']**2), \
                                     unit='kpc')
        
        # views to avoid typos
        X = self.tSim['X']
        Y = self.tSim['Y']
        vX = self.tSim['vX']
        vY = self.tSim['vY']
        vPhi = (Y*vX - X*vY) / self.tSim['R'] # same convention as SL2011

        self.tSim['vPhi'] = Column(vPhi, unit='km/s')

    def assignFlatUncertainty(self):

        """Takes the best-case proper motion uncertainty and estimates
        vphi uncertainty. All stars are assumed to be along the
        Sun-Galactocenter line, so that the distance used is just
        |R_star - R_Sun|"""

        dist = np.abs(self.tSim['R'] - self.RSol)

        self.tSim['e_vPhi_Flat'] = 4.74 * dist * self.uncPM

    def assignObsVPhi(self):

        """Creates an "observed" vphi column out of the errors"""
        
        # What is measured is the proper motion from the RELATIVE
        # velocity. So we have 

        # Initialise the new column, whatever happens
        deltaV = np.zeros(len(self.tSim))

        if self.useFlatUncertainty:
            deltaV = np.random.normal(size=len(self.tSim)) \
                * self.tSim['e_vPhi_Flat'] + 0.

            print np.min(deltaV), np.max(deltaV)

        self.tSim['vPhiObs'] = self.tSim['vPhi'] + deltaV

    def selectAsL11(self):

        """Applies the same selection criteria as Loebman et al. 2011
        Figure 10 top-left panel"""

        zAbs = np.abs(self.tSim['Z'])
        bZ = (zAbs > 0.5) & (zAbs < 1.0)
        bR = ( self.tSim['R'] > 7.0 ) & ( self.tSim['R'] < 9.0 )

        self.bSel = (self.bGood) & (bZ) & (bR) #& (self.tSim['Age'] < 2.)

    def selectForFitting(self):

        """Applies the selection criteria we want to use"""

        zAbs = np.abs(self.tSim['Z'])
        bZ = (zAbs >= self.ZMin) & (zAbs < self.ZMax)
        bR = ( self.tSim['R'] > self.RMin ) & ( self.tSim['R'] < self.RMax )
        bAge = ( self.tSim['Age'] > self.AgeMin ) \
            & ( self.tSim['Age'] < self.AgeMax )

        self.bSel = (self.bGood) & (bZ) & (bR) & (bAge)
        

    def buildStripsFeH(self):

        """Builds strips in Fe/H over which to perform the averaging"""
        
        self.stripsFeH = np.linspace(self.minFeH, self.maxFeH, \
                                         self.nStripsFeH+1, endpoint=True)
        
    def getStripStatistics(self, yKey='vPhi', nMin=10):

        """For each of the strips, get the strip statistics"""

        if np.size(self.stripsFeH) < 1:
            self.buildStripsFeH()

        # may as well loop through!!

        # View of what we're using for our vertical quantity
        x = self.tSim['FeH']
        y = self.tSim[yKey]

        nStrips = np.size(self.stripsFeH) - 1
        self.stripCounts = np.zeros(nStrips, dtype='int')
        self.stripMeans = np.zeros(nStrips)
        self.stripMedns = np.zeros(nStrips)
        self.stripStdds = np.zeros(nStrips)
        self.stripFeHs = np.zeros(nStrips) # central point for sample

        for iStrip in range(nStrips):
            xLo = self.stripsFeH[iStrip]
            xHi = self.stripsFeH[iStrip+1]

            bStrip = (self.bSel) & (x >= xLo) & (x < xHi)

            self.stripCounts[iStrip] = np.sum(bStrip)
            if self.stripCounts[iStrip] < nMin:
                continue
            
            self.stripMeans[iStrip] = np.mean(y[bStrip])
            self.stripMedns[iStrip] = np.median(y[bStrip])
            self.stripStdds[iStrip] = np.std(y[bStrip])
            self.stripFeHs[iStrip] = np.median(x[bStrip])

    def fitBrokenToStrips(self):

        """Fits broken-line to strip data"""

        # convenience views to avoid typos
        bStrip = (self.stripCounts > 10)
        if np.sum(bStrip) < 1:
            return

        x = self.stripFeHs[bStrip]
        y = self.stripMedns[bStrip]  # could come back to this later

        # guess set of parameters
        #guess = [-0.4, -40., -240., 40.]
        guess = [-0.3, 0.0, -250., 0.0]

        # Yes this could all be looped through...

        meritStraight = lambda pars, x, y: oneStraight(x, pars) - y
        meritBroken = lambda pars, x, y: twoStraight(x, pars) - y 

        # do the fitting 
        self.parsStraight, self.successStraight = \
            leastsq(meritStraight,guess[0:2] ,args=(x,y))

        self.parsBroken, self.successBroken = \
            leastsq(meritBroken,guess[:] ,args=(x,y))

        # compute the sum of residuals, over the strips (not the
        # stars)
        self.chisqStraight = np.sum(meritStraight(self.parsStraight, x, y)**2)
        self.chisqBroken = np.sum(meritBroken(self.parsBroken, x, y)**2)

    def showL11(self, sKey='vPhiObs'):

        """Plots loebman et al. 2011"""

        plt.figure(1, figsize=(8,4))
        plt.clf()

        plt.scatter(self.tSim['FeH'][self.bSel], \
                        self.tSim[sKey][self.bSel], \
                        alpha=0.25, s=4, edgecolor='None')

        # set the title
        sTitle = '(%.2f <= R < %.2f) ; (%.2f <= |Z| < %.2f); (%.1f <= Age < %.1f)' \
            % (self.RMin, self.RMax, self.ZMin, self.ZMax, self.AgeMin, self.AgeMax)

        if self.useFlatUncertainty:
            sTitle = '%s - PM error %.2f mas/yr' % (sTitle, self.uncPM)

        plt.suptitle(sTitle, fontsize=12)
        plt.xlabel(r"$\left[ \frac{Fe}{H} \right]$", fontsize=14)
        plt.ylabel(r"$v_{\phi}$, km s$^{-1}$", fontsize=14)

        bStrips = (self.stripCounts > 10)
        plt.errorbar(self.stripFeHs[bStrips], \
                         self.stripMeans[bStrips], \
                         yerr=self.stripStdds[bStrips], \
                         ecolor='k', fmt='yo', zorder=5)

        plt.scatter(self.stripFeHs[bStrips], \
                         self.stripMeans[bStrips], \
                        color=self.stripCounts[bStrips], \
                        s=36, edgecolor='y', \
                        cmap=plt.cm.get_cmap('cubehelix'), zorder=15)
        plt.colorbar()

        dum = plt.hist2d(self.tSim['FeH'][self.bSel], \
                        self.tSim[sKey][self.bSel], \
                             bins=(75, 75), \
                             range=[[-1.5,0.5], [-350., -50.]], \
                             alpha=0.5, zorder=2)
        plt.colorbar()

        plt.xlim(-1.5,0.5)
        plt.ylim(-50., -350.)

        # Couple of useful pieces to just see what the various lines
        # look like over the data
        xFine = np.linspace(-1.2, 0.3)
        showByHand = False
        if showByHand:
            pTry = [-0.4, -40., -240., 40.]
            plt.plot(xFine, twoStraight(xFine, pTry), 'k-', lw=2, zorder=25)

        showFit=True
        if showFit:
            plt.plot(xFine, oneStraight(xFine, self.parsStraight), \
                                            'k--', lw=2, zorder=25)

            plt.plot(xFine, twoStraight(xFine, self.parsBroken), \
                                            'k-', lw=2, zorder=25)


# =================== Fitting routines used on generic (x,y) data ====

def oneStraight(x, P):

    """Single straight line"""

    return x*P[0] + P[1]

def twoStraight(x, P):

    """Double-line. Convention:

    P[0] = x at which the lines split

    P[1], P[2] = slope and intercept of the 'lower' line; 

    P[3] = slope of the 'upper' line. 

    No intercept for the upper line is specified because it is not a
    free parameter. The two sides must meet in the middle."""

    # Enforce the line-meeting condition.
    interceptHi = P[0] * (P[1] - P[3]) + P[2]

    bLo = (x < P[0])
    y = np.zeros(np.size(x))
    y[bLo] = P[1]*x[bLo] + P[2]
    y[~bLo] = P[3]*x[~bLo] + interceptHi

    return y


# ==================== Routines that use these objects and methods ===

def asciiToFits():

    """Reads from ascii, dumping the result to a fits file for rapid
    reading"""

    CA = ConvertAscii()
    CA.loadSim()
    CA.setPathBinary()
    CA.simToTable()


def testSimCalc(nStrips=10, maxFeH=0.1, eFlat=0.2, \
                    RMin=7., RMax=9., \
                    ZMin = 0.5, ZMax=1., \
                    AgeMin=0., AgeMax=15.):

    """Loads the fits simulation and calculates a couple of useful
    columns"""

    SS = SimSamples()
    SS.nStripsFeH = nStrips
    SS.maxFeH = maxFeH

    SS.RMin = RMin
    SS.RMax = RMax
    SS.ZMin = ZMin
    SS.ZMax = ZMax
    SS.AgeMin = AgeMin
    SS.AgeMax = AgeMax

    SS.uncPM = eFlat
    SS.useFlatUncertainty=True

    SS.loadFitsSim()
    SS.calcVphi()
    #SS.selectAsL11()
    SS.selectForFitting()

    SS.assignFlatUncertainty()
    SS.assignObsVPhi()

    SS.buildStripsFeH()
    SS.getStripStatistics('vPhiObs')

    SS.fitBrokenToStrips()
    print "Sum-of-squares:"
    print "Straight line: %.3f, 2 parameters" % (SS.chisqStraight)
    print "Broken line:   %.3f, 4 parameters" % ( SS.chisqBroken)

    SS.showL11()

#    print SS.tSim

#    print np.sum(SS.bGood)

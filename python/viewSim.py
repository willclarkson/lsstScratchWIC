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

class SimSamples(object):

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

        self.units['Age'] = 'Gy'
        self.units['Mass'] = '2.33e5 MSun'
        self.units['FeH'] = 'dex'
        self.units['alphaFe'] = 'dex'

    def loadSim(self):

        if not os.access(self.pathSim, os.R_OK):
            if self.Verbose:
                print "SimSamples.loadSim WARN - cannot read input path %s" \
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
#            print "SimSamples.loadSim INFO - importing ascii file..."
#            t0 = time.time()
#        self.tSim=Table.read(self.pathSim, data_start=2, format='ascii')
        
#        if self.Verbose:
#            t1 = time.time()
#            print "SimSamples.loadSimINFO - ... done after %.1f seconds" \
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

# ====================

def asciiToFits():

    """Reads from ascii, dumping the result to a fits file for rapid
    reading"""

    SS = SimSamples()
    SS.loadSim()
    SS.setPathBinary()
    SS.simToTable()


    #SS.dumpToFits()

#def fitsToTable():

#    """Converts the simulation from fits to fits-with-metadata"""

#    SS = SimSamples()
#    SS.loadFromFits()
#    SS.simToTable()
#    SS.setPathBinary()


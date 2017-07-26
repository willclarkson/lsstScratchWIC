#
# assembleUncertainties.py
#

# WIC 2017-07-25 - assembles the photometric and crowding
# uncertainties for an entire OpSim run, converting to flat table
# for convenient input to other routines. 

# Based on Peter Yoachim's CrowdingMetrics.ipynb which was then edited
# into 2017-07-25_AssembleCrowding.ipynb

# lsst stuff
import matplotlib.pyplot as plt
plt.ion()

import lsst.sims.maf.db as db
import lsst.sims.maf.metrics as metrics
import lsst.sims.maf.slicers as slicers
import lsst.sims.maf.metricBundles as metricBundles
import lsst.sims.maf.maps as maps

# pieces we need to extract spatial information
import healpy as hp
import healpyUtils
import numpy as np

# astropy manipulation
from astropy.table import Table, Column, join
from astropy.coordinates import SkyCoord
from astropy import units as u

# for testing the assembly of tables together
import glob, os

# low-tech timing
import time

def findUncertainties(thisFilter='r', \
                          nside=64, tMax=730, \
                          dbFil='minion_1016_sqlite.db', \
                          crowdError=0.2, \
                          seeingCol='FWHMeff'):

    """Catalogs the uncertainties for a given database, returns the
    file path"""

    opsdb = db.OpsimDatabase('minion_1016_sqlite.db')
    outDir = 'crowding_test_2017-07-25'
    resultsDb = db.ResultsDb(outDir=outDir)

    # slicer, etc.
    slicer = slicers.HealpixSlicer(nside=nside, useCache=False)
    sql = 'filter="%s" and night < %i' % (thisFilter, tMax)
    plotDict={'colorMax':27.}

    # build up the bundle list. First the crowding...
    bundleList = []
    metric = metrics.CrowdingMetric(crowding_error=0.05, seeingCol=seeingCol)
    bundle = metricBundles.MetricBundle(metric,\
                                            slicer,sql, plotDict=plotDict)
    bundleList.append(bundle)
    
    # ... then the m5col
    metricCoadd = metrics.Coaddm5Metric()
    bundleCoadd = metricBundles.MetricBundle(metricCoadd,\
                                                 slicer,sql,plotDict=plotDict)
    bundleList.append(bundleCoadd)
    
    # convert to the bundledict...
    bundleDict = metricBundles.makeBundlesDictFromList(bundleList)
    bgroup = metricBundles.MetricBundleGroup(bundleDict, \
                                                 opsdb, outDir=outDir, \
                                                 resultsDb=resultsDb)

    # ... and run...
    bgroup.runAll()

    # now produce the table for this run
    nameDepth = 'opsim_CoaddM5_%s_and_night_lt_%i_HEAL' \
        % (thisFilter, tMax)
    nameCrowd = 'opsim_Crowding_To_Precision_%s_and_night_lt_%i_HEAL' \
        % (thisFilter, tMax)

    npix = bgroup.bundleDict[nameDepth].metricValues.size
    nsideFound = hp.npix2nside(npix)
    ra, dec = healpyUtils.hpid2RaDec(nside, np.arange(npix))
    cc = SkyCoord(ra=np.copy(ra), dec=np.copy(dec), frame='fk5', unit='deg')

    # boolean mask for nonzero entries
    #bVal = ~bgroup.bundleDict[nameDepth].metricValues.mask

    # Generate the table
    tVals = Table()
    tVals['HEALPIX'] = np.arange(npix)
    tVals['RA'] = cc.ra.degree
    tVals['DE'] = cc.dec.degree
    tVals['l'] = cc.galactic.l.degree
    tVals['b'] = cc.galactic.b.degree

    sCoadd = '%sCoadd' % (thisFilter)
    sCrowd = '%sCrowd' % (thisFilter)

    tVals[sCoadd] = bgroup.bundleDict[nameDepth].metricValues
    tVals[sCrowd] = bgroup.bundleDict[nameCrowd].metricValues

    tVals['%sCrowdBri' % (thisFilter)] = \
        np.asarray(tVals[sCrowd] < tVals[sCoadd], 'int')

    # cut down by mask
    #tVals = tVals[bVal]

    # Set metadata and write to disk
    tVals.meta['nsideFound'] = nsideFound
    tVals.meta['tMax'] = tMax

    # generate output path
    pathTab = '%s/table_uncty_%s_%s_nside%i_tmax%i.fits' % \
        (outDir, dbFil.split('_sqlite')[0], thisFilter, nside, tMax)

    # save the table
    tVals.write(pathTab, overwrite=True)

    return pathTab

def wrapTables(nside=64, tMax=730, \
                          dbFil='minion_1016_sqlite.db', \
                          crowdError=0.2, \
                          seeingCol='FWHMeff', \
                   cleanNpz=True):
    
    """Wrapper - constructs the tables for each filter"""

    # list of paths
    lPaths = []

    for sFilt in ['u', 'g', 'r', 'i', 'z', 'y']:
        thisPath = findUncertainties(sFilt, \
                                         nside=nside, \
                                         tMax=tMax, \
                                         crowdError=crowdError, \
                                         seeingCol=seeingCol, \
                                         dbFil=dbFil)
        lPaths.append(thisPath)

    # fuse the tables
    dirOut = lPaths[0].split('/')[0]
    pathFused = '%s/fused_%s_n%i_t%i.fits.gz' % \
        (dirOut, dbFil.split('_sqlite.db')[0], \
             nside, tMax)

    if cleanNpz:
        for pathNp in glob.glob('%s/*.npz' % (dirOut)):
            os.remove(pathNp)

    print lPaths
    print pathFused
    fuseTables(lPaths, pathFused, removeAfterReading=True)

def fuseTables(lPaths=[], pathFused='testFused.fits', \
                   removeAfterReading=False):

    """Fuses the tables into an output"""

    # for debugging
    if len(lPaths) < 1:
        lPaths= glob.glob('./crowding_test_2017-07-25/table_uncty*fits')

    # list of tables read in
    tMaster = Table()
    for thisPath in lPaths:
        thisTable = Table.read(thisPath)

        # to save disk space
        if removeAfterReading:
            os.remove(thisPath)

        print len(thisTable)

        if len(tMaster.colnames) < 1:
            tMaster = thisTable
        else:
            tMaster = join(tMaster, thisTable)
        
    # Don't forget to actually write to disk!
    tMaster.write(pathFused, overwrite=True)
                      

def wrapThruDatabases(nside=128, tMax=9999):

    """Loops through databases, producing a fused table for each"""

    for dbFil in ['minion_1016_sqlite.db', \
                      'astro_lsst_01_1004_sqlite.db']:

        wrapTables(nside=nside, tMax=tMax, \
                       dbFil=dbFil)

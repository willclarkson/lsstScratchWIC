#
# assembleUncertainties.py
#

# WIC 2017-07-25 - assembles the photometric and crowding
# uncertainties for an entire OpSim run, converting to flat table for
# convenient input to other routines. Written for work with Oscar
# Gonzalez during STFC visit at ROE.

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

# to be able to specify which figures we want
import lsst.sims.maf.plots as plots


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
                          seeingCol='FWHMeff', \
                          cleanNpz=True, \
                          doPlots=False):

    """Catalogs the uncertainties for a given database, returns the
    file path"""

    # doPlots switches on plotting. This makes things quite a bit
    # slower for coarse healpix, and I haven't worked out how to
    # specify the output plot directory yet. Recommend default to
    # False.

    # plot functions
    plotFuncs = [plots.HealpixSkyMap(), plots.HealpixHistogram()]

    opsdb = db.OpsimDatabase(dbFil)
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
                                            slicer,sql, plotDict=plotDict, \
                                            plotFuncs=plotFuncs)
    bundleList.append(bundle)
    
    # ... then the m5col
    metricCoadd = metrics.Coaddm5Metric()
    bundleCoadd = metricBundles.MetricBundle(metricCoadd,\
                                                 slicer,sql,plotDict=plotDict, \
                                                 plotFuncs=plotFuncs)
    bundleList.append(bundleCoadd)
    
    # Let's also pass through some useful statistics
    # per-HEALPIX. We'll want to bring across the output metric names
    # as well so that we can conveniently access them later.
    # some convenient plot functions
    statsCols = ['FWHMeff', 'fiveSigmaDepth', 'airmass']
    metricNames = [ 'MedianMetric', 'RobustRmsMetric' ]
    statsNames = {}
    sKeyTail = '_%s_and_night_lt_%i_HEAL' % (thisFilter, tMax)

    # may as well get good plot dicts too...
    plotDicts = {}
    plotDicts['FWHMeff_MedianMetric'] = {'colorMax':2.}
    plotDicts['fiveSigmaDepth_MedianMetric'] = {'colorMax':26.}
    plotDicts['airmass_MedianMetric'] = {'colorMax':2.5}
    plotDicts['FWHMeff_RobustRmsMetric'] = {'colorMax':1.}
    plotDicts['fiveSigmaDepth_RobustRmsMetric'] = {'colorMax':2.}
    plotDicts['airmass_RobustRmsMetric'] = {'colorMax':1.}

    # ensure they all have xMax as well
    for sKey in plotDicts.keys():
        plotDicts[sKey]['xMax'] = plotDicts[sKey]['colorMax']

    for colName in statsCols:
        for metricName in metricNames:

            # lift out the appropriate plotdict
            plotDict = {}
            sDict = '%s_%s' % (colName, metricName)
            if sDict in plotDicts.keys():
                plotDict = plotDicts[sDict]

            thisMetric = getattr(metrics, metricName)
            metricObj = thisMetric(col=colName)
            bundleObj = metricBundles.MetricBundle(metricObj,slicer,sql, \
                                                       plotDict=plotDict, \
                                                       plotFuncs=plotFuncs)
            bundleList.append(bundleObj)

            # construct the output table column name and the key for
            # the bundle object
            tableCol = '%s%s_%s' % (thisFilter, colName, metricName)
            statsNames[tableCol] = 'opsim_%s_%s%s' \
                % (metricName.split('Metric')[0], colName, sKeyTail)
        
            # as a debug, see if this is actually working...
            # print tableCol, statsNames[tableCol], statsNames[tableCol]

    # try the number of visits
    col2Count = 'fiveSigmaDepth'
    metricN = metrics.CountMetric(col=col2Count)
    bundleN = metricBundles.MetricBundle(metricN, slicer, sql, \
                                             plotFuncs=plotFuncs)
    bundleList.append(bundleN)
    countCol = '%sCount' % (thisFilter)
    statsNames[countCol] = 'opsim_Count_%s%s' % (col2Count, sKeyTail)

    # convert to the bundledict...
    bundleDict = metricBundles.makeBundlesDictFromList(bundleList)
    bgroup = metricBundles.MetricBundleGroup(bundleDict, \
                                                 opsdb, outDir=outDir, \
                                                 resultsDb=resultsDb)

    # ... and run...
    bgroup.runAll()

    # ... also plot...
    if doPlots:
        bgroup.plotAll()

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
    bVal = ~bgroup.bundleDict[nameDepth].metricValues.mask

    # Generate the table
    tVals = Table()
    tVals['HEALPIX'] = np.arange(npix)
    tVals['RA'] = cc.ra.degree
    tVals['DE'] = cc.dec.degree
    tVals['l'] = cc.galactic.l.degree
    tVals['b'] = cc.galactic.b.degree

    sCoadd = '%sCoadd' % (thisFilter)
    sCrowd = '%sCrowd' % (thisFilter)

    tVals[sCoadd] = Column(bgroup.bundleDict[nameDepth].metricValues, \
                               dtype='float')
    tVals[sCrowd] = Column(bgroup.bundleDict[nameCrowd].metricValues, \
                               dtype='float')

    # enforce rounding. Three decimal places ought to be sufficient
    # for most purposes. See if the Table constructor follows this
    # through. (DOESN'T SEEM TO WORK when writing to fits anyway...)
    tVals[sCoadd].format='%.3f'
    tVals[sCrowd].format='%.2f'  # (may only get reported to 1 d.p. anyway)

    #tVals['%sCrowdBri' % (thisFilter)] = \
    #    np.asarray(tVals[sCrowd] < tVals[sCoadd], 'int')

    # add the mask as a boolean
    tVals['%sGood' % (thisFilter)] = \
        np.asarray(bVal, 'int')

    # now add all the summary statistics for which we asked. Try
    # specifying the datatype
    for sStat in statsNames.keys():
        tVals[sStat] = Column(\
            bgroup.bundleDict[statsNames[sStat]].metricValues, \
                dtype='float')

    tVals[countCol] = Column(bgroup.bundleDict[statsNames[countCol]].metricValues, dtype='int')

    # cut down by mask
    #tVals = tVals[bVal]

    # Set metadata and write to disk. Add comments later.
    tVals.meta['nsideFound'] = nsideFound
    tVals.meta['tMax'] = tMax
    tVals.meta['crowdError'] = crowdError
    tVals.meta['countedCol'] = col2Count[:]

    # generate output path
    pathTab = '%s/table_uncty_%s_%s_nside%i_tmax%i.fits' % \
        (outDir, dbFil.split('_sqlite')[0], thisFilter, nside, tMax)

    # save the table
    tVals.write(pathTab, overwrite=True)

    # give this method the capability to remove the npz file (useful
    # if we want to go to very high spatial resolution for some
    # reason):
    if cleanNpz:
        for pathNp in glob.glob('%s/*.npz' % (outDir)):
            os.remove(pathNp)

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
    outDir = lPaths[0].split('/')[0]

    # string for crowding error
    sCrowd = '%s' % (str(crowdError).replace('.','p'))
    
    pathFused = '%s/fused_%s_n%i_t%i_e%s.fits.gz' % \
        (outDir, dbFil.split('_sqlite.db')[0], \
             nside, tMax, sCrowd)

    if cleanNpz:
        for pathNp in glob.glob('%s/*.npz' % (outDir)):
            os.remove(pathNp)

    print lPaths
    print pathFused
    fuseTables(lPaths, pathFused, removeAfterReading=True)

def fuseTables(lPaths=[], pathFused='testFused.fits', \
                   removeAfterReading=False, \
                   keepGoodOnly=True):

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
      
    # keep only the good rows?
    if keepGoodOnly:
        bGood = tMaster['uGood'] > 0
        for sFilt in ['g', 'r', 'i', 'z', 'y']:
            sCol = '%sGood' % (sFilt)
            if not sCol in tMaster.colnames:
                continue

            bGood = (bGood) & (tMaster[sCol] > 0)

        tMaster = tMaster[bGood]
        tMaster.meta['HISTORY'] = 'Selected on "good" entries for all filters'

    # Don't forget to actually write to disk!
    tMaster.write(pathFused, overwrite=True)
                      

def wrapThruDatabases(nside=128, tMax=9999, crowdError=0.05):

    """Loops through databases, producing a fused table for each"""

    for dbFil in ['minion_1016_sqlite.db', \
                      'astro_lsst_01_1004_sqlite.db']:

        wrapTables(nside=nside, tMax=tMax, \
                       dbFil=dbFil, \
                       crowdError=crowdError)
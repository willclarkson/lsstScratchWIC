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
                          doPlots=False, \
                          wrapGalacs=True, \
                          selectStrip=True):
#, \
#                          hiRes=True):

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

    # initialise the entire bundle list
    bundleList = []

    # set up for higher-resolution spatial maps DOESN'T WORK ON LAPTOP
    #if hiRes:
    #    mafMap = maps.StellarDensityMap(nside=128)
    #else:
    #    mafMap = maps.StellarDensityMap(nside=64)

    # if passed a single number, turn the crowdErr into a list
    if str(crowdError.__class__).find('list') < 0:
        crowdVals = [np.copy(crowdError)]
    else:
        crowdVals = crowdError[:]

    # build up the bundle list. Build up a list of crowding values and
    # their column names. HARDCODED for the moment, can make the input list
    # an argument if desired.
    crowdStem = '%sCrowd' % (thisFilter)
    lCrowdCols = []
    # loop through the crowding values
    #crowdVals = [0.2, 0.1, 0.05]
    for errCrowd in crowdVals:  
        crowdName = '%s%.3f' % (crowdStem,errCrowd)
        lCrowdCols.append(crowdName) # to pass later
        metricThis = metrics.CrowdingMetric(crowding_error=errCrowd, \
                                                seeingCol='FWHMeff')
        bundleThis = metricBundles.MetricBundle(metricThis, slicer, sql, \
                                                    plotDict=plotDict, \
                                                    fileRoot=crowdName, \
                                                    runName=crowdName, \
                                                    plotFuncs=plotFuncs)

        bundleList.append(bundleThis)

    #metric = metrics.CrowdingMetric(crowding_error=crowdError, \
    #    seeingCol=seeingCol)
    #bundle = metricBundles.MetricBundle(metric,\
    #                                        slicer,sql, plotDict=plotDict, \
    #                                        plotFuncs=plotFuncs)
    #bundleList.append(bundle)
    
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
    metricNames = [ 'MedianMetric', 'RobustRmsMetric', 'MinMetric', 'MaxMetric']
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

    # initialize the minmax values for the moment
    plotDicts['FWHMeff_MinMetric'] = {'colorMax':3}
    plotDicts['FWHMeff_MaxMetric'] = {'colorMax':3}

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

    # wrap Galactics?
    if wrapGalacs:
        bBig = tVals['l'] > 180.
        tVals['l'][bBig] -= 360.

    sCoadd = '%sCoadd' % (thisFilter)
    sCrowd = '%sCrowd' % (thisFilter)

    tVals[sCoadd] = Column(bgroup.bundleDict[nameDepth].metricValues, \
                               dtype='float')

    # REPLACE the single-crowding with the set of columns, like so:
    #tVals[sCrowd] = Column(bgroup.bundleDict[nameCrowd].metricValues, \
    #                           dtype='float')

    for colCrowd in lCrowdCols:
        tVals[colCrowd] = Column(bgroup.bundleDict[colCrowd].metricValues, \
                                     dtype='float', format='%.3f')

    # enforce rounding. Three decimal places ought to be sufficient
    # for most purposes. See if the Table constructor follows this
    # through. (DOESN'T SEEM TO WORK when writing to fits anyway...)
    tVals[sCoadd].format='%.3f'
    #tVals[sCrowd].format='%.2f'  # (may only get reported to 1 d.p. anyway)

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
    tVals.meta['crowdError'] = crowdVals
    tVals.meta['countedCol'] = col2Count[:]

    # Can select only within strip to cut down on space requirements
    sSel=''
    if selectStrip:
        bMin = -30.
        bMax = +25.
        lMin = -150.
        lMax = 80.
        sSel = '_nrPlane'

        bStrip = (tVals['b'] >= bMin) & \
            (tVals['b'] <= bMax) & \
            (tVals['l'] >= lMin) & \
            (tVals['l'] <= lMax)

        tVals = tVals[bStrip]

        tVals.meta['sel_lMin'] = lMin
        tVals.meta['sel_lMax'] = lMax
        tVals.meta['sel_bMin'] = bMin
        tVals.meta['sel_bMax'] = bMax

    # metadata
    tVals.meta['selectStrip'] = selectStrip

    # generate output path
    pathTab = '%s/table_uncty_%s_%s_nside%i_tmax%i%s.fits' % \
        (outDir, dbFil.split('_sqlite')[0], thisFilter, nside, tMax, sSel)

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
                          crowdError=[0.2, 0.1, 0.05], \
                          seeingCol='FWHMeff', \
                   cleanNpz=True, \
                   selectPlane=False):
    
    """Wrapper - constructs the tables for each filter"""

    # list of paths
    lPaths = []

    for sFilt in ['u', 'g', 'r', 'i', 'z', 'y']:
        thisPath = findUncertainties(sFilt, \
                                         nside=nside, \
                                         tMax=tMax, \
                                         crowdError=crowdError, \
                                         seeingCol=seeingCol, \
                                         dbFil=dbFil, \
                                         selectStrip=selectPlane)
        lPaths.append(thisPath)

    # fuse the tables
    outDir = lPaths[0].split('/')[0]

    # string for crowding error. This could be made a bit better using
    # the actual table metadata. For the moment, take the input.
    try:
        minCrowd = '%.3f' % (np.min(crowdError))
        maxCrowd = '%.3f' % (np.max(crowdError))
        sCrowd = 'cErr%s-%s' % (minCrowd, maxCrowd)
        sCrowd = sCrowd.replace('.','p')
    except:
        sCrowd = '%s' % (str(crowdError).replace('.','p'))

        # in case an array is still getting passed here...
        sCrowd = sCrowd.replace('[','').replace(']',''),replace(' ','-')
    
    # Did we select close to the plane?
    sPlane = ''
    if selectPlane:
        sPlane='_nrPlane'

    pathFused = '%s/fused_%s_n%i_t%i_e%s%s.fits.gz' % \
        (outDir, dbFil.split('_sqlite.db')[0], \
             nside, tMax, sCrowd, sPlane)

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
                      

def wrapThruDatabases(nside=128, tMax=9999, \
                          crowdError=[0.2, 0.1, 0.05, 0.01], \
                          selectPlane=False):

    """Loops through databases, producing a fused table for each. Example call:

    assembleUncertainties.wrapThruDatabases(crowdError=[0.2,0.1,0.05,0.02])"""

    for dbFil in ['minion_1016_sqlite.db', \
                      'astro_lsst_01_1004_sqlite.db']:

        wrapTables(nside=nside, tMax=tMax, \
                       dbFil=dbFil, \
                       crowdError=crowdError, \
                       selectPlane=selectPlane)

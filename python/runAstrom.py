
### runAstrom.py -- hacked out of Peter Yoachim's
### ScratchStuff/runAstrometry/runAstrom.py 
###
### with loops shoved in to run a set of cases for LSST whitepaper.

### Tweaks 2016-05-01: try using spearman-r and pearson-r for two year
### metrics to address suggestion from Monet. To achieve this, use the
### following arguments:
###
### runAstrom.go(DoRun=True, checkCorrKind=True)

### ---

### wfdPlane added as an argument. To do all three runs in Observing
### Strategy Chapter 4, do the following:

### for wfd in [False, True]:
####      runAstrom(go=True, wfd)

### ---

### NOTES 2016-04-23 This is a sequence of updates that I made while
### testing under various circumstances. In many cases I did not
### delete the old settings, just re-defined them in subsequent
### lines. I make no guarantees that the result will be easy to read.

#### Just as a point of reference, running this all through once took
#### 228 minutes on my 2013-era Macbook Air (4GB, 1.7 GHz).

import matplotlib.pyplot as plt
import lsst.sims.maf.db as db
import lsst.sims.maf.metrics as metrics
import lsst.sims.maf.slicers as slicers
import lsst.sims.maf.metricBundles as metricBundles
import lsst.sims.maf.plots as plots
import healpy as hp

from lsst.sims.maf.metrics import calibrationMetrics

# A couple of standard modules
import os, time, copy

# Run the Astrometry metics on a number of runs

# WIC - I prefer to use this within a routine so we can test importing
# before testing running...
def go(nside=64, rmag=21., SedTemplate='flat', DoRun=False, LFilters = [], \
           LNightMax=[], nightMax=1e4, \
           CustomPlotLimits=True, \
           RunOne=False, MaxRuns=1e3, \
           SpatialClip=95., \
           seeingCol='FWHMeff', \
           sCmap='cubehelix_r', \
           checkCorrKind=False, \
           wfdPlane=True):

    # Go to the directory where the sqlite databases are held...

    # cd /Users/clarkson/Data/LSST/OpSimRuns/opsim20160411


    # WIC 2015-12-29 - set up for a master-run with all cases, this time with plotting limits
    # Break the specifications across lines to make subdivision easier
    
    # Subsets by time first, then by filter, finally the whole shebang

    # 2016-04-23 - replaced enigma_1189 --> minion_1016
    # 2016-04-23 - replaced ops2_1092 --> minion_1020
    
    
    # (Yes the inversion of the first two is deliberate.)
    runNames = ['minion_1016', 'minion_1020', 'minion_1020', 'minion_1016', \
                    'minion_1020', 'minion_1016', 'minion_1020', 'minion_1016', \
                    'minion_1020', 'minion_1016']
    LFilters = ['', '', '', '', \
                    'u', 'u', 'y', 'y', \
                    '', '']  
    LNightMax = [365, 365, 730, 730, \
                     1e4, 1e4, 1e4, 1e4, \
                     1e4, 1e4]

    # WIC try again, this time on the new astro_lsst_01_1004 only
    if wfdPlane:
        LFilters = ['', '', '', 'u', 'y']  
        LNightMax = [365, 730, 1e4, 1e4, 1e4]
        runNames = ['astro_lsst_01_1004' for i in range (len(LFilters)) ]

    # WIC 2016-05-01 check correlation
    if checkCorrKind:
        LFilters = ['', '']
        LNightMax = [365, 365]
        runNames = ['minion_1016', 'minion_1016']

        # Type of correlation used for HA Degen 
        # checkCorrKind = True
        useSpearmanR = [False, True]
    
    # List of upper limits to parallax and proper motion error. For parallax, 3.0 mas is probably good
    LUpperParallax = []
    LUpperPropmotion = []


    if CustomPlotLimits:
    
        LUpperParallax = [10, 10, 10, 10, \
                              10, 10, 40, 40, \
                              3.0, 3.0 ]

    
        # For proper motion, it's a little tricky to say because the
        # regular case is so pathological for the field. Try the following:
        LUpperPropmotion = [40, 40, 5, 20, \
                                3.5, 20, 3.5, 20, \
                                0.5, 5]

        if len(runNames) < 2:
            LUpperPropmotion = [100 for i in range(len(runNames))]

    print "runAstrom.go INFO - will run the following:"
    for iSho in range(len(runNames)):
        print "%i: %-12s, %1s, %i" % (iSho, runNames[iSho], LFilters[iSho], LNightMax[iSho])
    print "==========================="

    print "mag max = %.2f" % (rmag)
    print "---------------------------"

#    print runNames
#    if not DoRun:
#        print "Set DoRun=True to actually run this."
#        print len(LFilters), len(runNames), len(LFilters) == len(runNames)
#        return

#'kraken_1038', 'kraken_1034', 'ops2_1098']


    # nside = 64

    slicer = slicers.HealpixSlicer(nside=nside)

    # Make it so we don't bother with the silly power spectra
    plotFuncs = [plots.HealpixSkyMap(), plots.HealpixHistogram()]

    # WIC - back up the plotting arguments with a default value
    plotFuncsPristine = copy.deepcopy(plotFuncs)

    # WIC - the only way this will make sense to me is if I make a
    # dictionary of plot arguments. Let's try it...
    DPlotArgs = {}
    for plotArg in ['parallax', 'propmotion', 'coverage', 'HAdegen']:
        DPlotArgs[plotArg] = copy.deepcopy(plotFuncs)

    if CustomPlotLimits:

        # Use the same color map for all the metrics
        for plotMetric in DPlotArgs.keys():
            DPlotArgs[plotMetric][0].defaultPlotDict['cmap'] = sCmap


        # Apply spatial clipping for all but the HADegen, for which we
        # have other limits...
        for plotMetric in ['parallax', 'propmotion', 'coverage']:
            DPlotArgs[plotMetric][0].defaultPlotDict['percentileClip'] = SpatialClip

        # Some limits common to spatial maps and histograms
        for iPl in range(0,2):
            DPlotArgs['propmotion'][iPl].defaultPlotDict['logScale'] = True

        # NOT a loop because we might want to separate out the behavior

        # Standardized range for the histograms for new parallax metrics
        DPlotArgs['coverage'][1].defaultPlotDict['xMin'] = 0.
        DPlotArgs['coverage'][1].defaultPlotDict['xMax'] = 1.
        DPlotArgs['HAdegen'][1].defaultPlotDict['xMin'] = -1.
        DPlotArgs['HAdegen'][1].defaultPlotDict['xMax'] =  1.
            
        # Standardize the sky map for the HAdegen as well.
        DPlotArgs['coverage'][1].defaultPlotDict['xMin'] = 0.
        DPlotArgs['coverage'][1].defaultPlotDict['xMax'] = 1.
        DPlotArgs['HAdegen'][0].defaultPlotDict['xMin'] = -1.
        DPlotArgs['HAdegen'][0].defaultPlotDict['xMax'] =  1.


        # Standardize at least the lower bound of the histogram in
        # both the proper motion and parallax errors. Upper limit we
        # can customize with a loop.
        DPlotArgs['propmotion'][1].defaultPlotDict['xMin'] = 1e-2  # should not be zero if log scale!!
        DPlotArgs['parallax'][1].defaultPlotDict['xMin'] = 0.


    # WIC - try changing the plot dictionary

    if not DoRun:
        plotFuncs[0].defaultPlotDict['logScale'] = True
        print DPlotArgs['propmotion'][0].defaultPlotDict
        print DPlotArgs['propmotion'][1].defaultPlotDict
        
        return

    # The old runs have the seeing in finSeeing
    #seeingCol = 'finSeeing'

    ### UPDATE THE SEEING COLUMN
    #seeingCol = 'FWHMeff'   ## Moved up to a command-line argument


    # Use all the observations. Can change if you want a different
    # time span
    # sqlconstraint = ''

    # list of sqlconstraints now used, which gets handled within the loop.

    # run some summary stats on everything
    summaryMetrics = [metrics.MedianMetric()]

    tStart = time.time()

    # Running one, or the whole lot?
    RunMax = len(runNames)

    # allow user to set a different number (say, 2)
    if MaxRuns < RunMax and MaxRuns > 0:
        RunMax = int(MaxRuns)

    # the following keyword overrides
    if RunOne:
        RunMax = 1

    print "Starting runs. RunMax = %i" % (RunMax)

    for iRun in range(RunMax):
        run = runNames[iRun][:]

    # for run in runNames:
        # Open the OpSim database
        timeStartIteration = time.time()

        # Some syntax added to test for existence of the database
        dbFil = run+'_sqlite.db'
        if not os.access(dbFil, os.R_OK):
            print "runAstrom.go FATAL - cannot acces db file %s" % (dbFil)
            print "runAstrom.go FATAL - skipping run %s" % (run)
            continue
    
        else:
            deltaT = time.time()-tStart
            print "runAstrom.go INFO - ##################################"
            print "runAstrom.go INFO - starting run %s with nside=%i after %.2f minutes" \
                % (run, nside, deltaT/60.)

        opsdb = db.OpsimDatabase(run+'_sqlite.db')

        # Set SQL constraint appropriate for each filter in the
        # list. If we supplied a list of filters, use it for 
        sqlconstraint = ''
        ThisFilter = 'ugrizy'
        if len(LFilters) == len(runNames):

            # Only change the filter if one was actually supplied!
            if len(LFilters[iRun]) == 1:
                ThisFilter = LFilters[iRun]
                sqlconstraint = 'filter = "%s"' % (ThisFilter)

        # If nightmax was supplied, use it 
        ThisNightMax = int(nightMax)  # copy not view
        if len(LNightMax) == len(runNames):

            # Only update nightmax if one was given
            try:
                ThisNightMax = int(LNightMax[iRun])  # This might be redundant with the fmt statement below.
                if len(sqlconstraint) < 1:
                    sqlconstraint = 'night < %i' % (ThisNightMax)
                else:
                    sqlconstraint = '%s and night < %i' % (sqlconstraint, ThisNightMax)
            except:
                print "runAstrom.go WARN - run %i problem with NightMax" % (iRun)
                dumdum = 1.

        # Set where the output should go - include the filter!! 
        sMag = '%.1f' % (rmag)
        sMag = sMag.replace(".","p")
        outDir = './metricEvals/%s_nside%i_%s_n%i_r%s' % (run, nside, ThisFilter, ThisNightMax, sMag)

        # Ensure we'll be able to find this later on...
        if CustomPlotLimits:
            outDir = '%s_lims' % (outDir)

        # if we are testing the kind of correlation used, include that
        # in the output here.
        if checkCorrKind:
            if useSpearmanR[iRun]:
                sCorr = 'spearmanR'
            else:
                sCorr = 'pearsonR'
        
            outDir = '%s_%s' % (outDir, sCorr)

        # From this point onwards, stuff actually gets run. This is
        # the place to output what will actually happen next.
        print "runAstrom.go INFO - about to run:"
        print "runAstrom.go INFO - sqlconstraint: %s ; run name %s ; nside %i" % (sqlconstraint, run, nside)
        print "runAstrom.go INFO - output directory will be %s" % (outDir)
        if not DoRun:
            continue

        # ensure the output directory actually exists...
        if not os.access(outDir, os.R_OK):
            print "runAstrom.go INFO - creating output directory %s" % (outDir)
            os.makedirs(outDir)


        resultsDb = db.ResultsDb(outDir=outDir)
        bundleList = []

        # WIC - to make this at least somewhat uniform, build the plot
        # functions including arguments out of our copies above.
        plotFuncsPropmotion = copy.deepcopy(DPlotArgs['propmotion'])
        plotFuncsParallax = copy.deepcopy(DPlotArgs['parallax'])
        plotFuncsCoverage = copy.deepcopy(DPlotArgs['coverage'])
        plotFuncsHAdegen = copy.deepcopy(DPlotArgs['HAdegen'])

        # if using custom plot limits, will want to include the limits
        # for proper motion and parallax too... programming a bit defensively 
        # here, including an extra check (rather than just the length of the lists 
        # above). 
        if CustomPlotLimits:
            if len(LUpperParallax) == len(runNames):
                plotFuncsParallax[1].defaultPlotDict['xMax'] = float(LUpperParallax[iRun])

            if len(LUpperPropmotion) == len(runNames):
                plotFuncsPropmotion[1].defaultPlotDict['xMax'] = float(LUpperPropmotion[iRun])

        # Configure the metrics
        metric = metrics.ParallaxMetric(rmag=rmag, seeingCol=seeingCol, SedTemplate=SedTemplate)
        bundle = metricBundles.MetricBundle(metric, slicer, sqlconstraint, runName=run,
#                                            plotFuncs=plotFuncs, \
                                                plotFuncs = plotFuncsParallax, \
                                                summaryMetrics=summaryMetrics)
        bundleList.append(bundle)

        metric=metrics.ProperMotionMetric(rmag=rmag, seeingCol=seeingCol, SedTemplate=SedTemplate)
        bundle = metricBundles.MetricBundle(metric, slicer, sqlconstraint, runName=run,
#                                            plotFuncs=plotFuncs, \
                                                plotFuncs=plotFuncsPropmotion, \
                                                summaryMetrics=summaryMetrics)
        bundleList.append(bundle)

        metric = calibrationMetrics.ParallaxCoverageMetric(rmag=rmag, seeingCol=seeingCol, SedTemplate=SedTemplate)
        bundle = metricBundles.MetricBundle(metric, slicer, sqlconstraint, runName=run,
#                                            plotFuncs=plotFuncs, \
                                                plotFuncs=plotFuncsCoverage, \
                                                summaryMetrics=summaryMetrics)
        bundleList.append(bundle)

        # Now for the HA Degen metric. If testing the type of
        # correlation, call the metric differently here. Since the
        # argument to actually do this is only part of my github fork
        # at the moment, we use a different call. Running with default
        # arguments (checkCorrKind=False) should then work without
        # difficulty.
        metric = calibrationMetrics.ParallaxHADegenMetric(rmag=rmag, seeingCol=seeingCol, SedTemplate=SedTemplate)
        if checkCorrKind:
            metric = calibrationMetrics.ParallaxHADegenMetric(rmag=rmag, seeingCol=seeingCol, SedTemplate=SedTemplate, useSpearmanR=useSpearmanR[iRun])
            print "TESTING CORRELATION KIND -- useSpearmanR", useSpearmanR[iRun]
            

        bundle = metricBundles.MetricBundle(metric, slicer, sqlconstraint, runName=run,
#                                            plotFuncs=plotFuncs, \
                                                plotFuncs=plotFuncsHAdegen, \
                                                summaryMetrics=summaryMetrics)
        bundleList.append(bundle)

        # Run everything and make plots
        bundleDict = metricBundles.makeBundlesDictFromList(bundleList)
        bgroup = metricBundles.MetricBundleGroup(bundleDict, opsdb, outDir=outDir, resultsDb=resultsDb)
#        try:
        bgroup.runAll()

        print "runAstrom.go INFO - bundles took %.2f minutes" \
            % ((time.time() - timeStartIteration) / 60.)

#        except KeyboardInterrupt:
#            print "runAstrom.go FATAL - keyboard interrupt detected. Halting."
#            return
        bgroup.plotAll()

        print "runAstrom.go INFO - bundles + plotting took %.2f minutes" \
            % ((time.time() - timeStartIteration) / 60.)
        

    print "Finished entire set. %i runs took %.2f minutes." % (iRun + 1, (time.time()-tStart)/60.)

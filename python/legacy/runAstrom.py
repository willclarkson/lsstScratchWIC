import matplotlib.pyplot as plt
import lsst.sims.maf.db as db
import lsst.sims.maf.metrics as metrics
import lsst.sims.maf.slicers as slicers
import lsst.sims.maf.metricBundles as metricBundles
import lsst.sims.maf.plots as plots
import healpy as hp

# A couple of standard modules
import os, time, copy

# Run the Astrometry metics on a number of runs

# WIC - I prefer to use this within a routine so we can test importing
# before testing running...
def go(nside=64, rmag=20., SedTemplate='flat', DoRun=False, LFilters = [], \
           LNightMax=[], nightMax=1e4, \
           CustomPlotLimits=True, \
           RunOne=False, MaxRuns=1e3, \
           SpatialClip=95.):

    # runNames = ['enigma_1189', 'ops2_1093']

    # runNames
    #runNames = ['ops2_1092', 'kraken_1038', 'kraken_1034', 'ops2_1098']
    #runNames = ['kraken_1038', 'kraken_1034', 'ops2_1098']

    # 2015-12-23 - put kraken_1038 at the end, it seems to run
    # extremely slowly...
    runNames = ['enigma_1189', 'ops2_1098', 'kraken_1034', 'kraken_1038']

    runNames = ['ops2_1092', 'kraken_1033', 'enigma_1271']

    # UPDATE - ops2_1092 ran quite quickly on nside=32... rerun on 64

    runNames = ['ops2_1092', 'enigma_1189', 'enigma_1271', 'kraken_1038']
    
    # UPDATE 2015-12-28 -- run with single-filter choices, compare
    # enigma to ops2_1092

    # WIC 2015-12-28 -- try with single-filter and all then small subset
    runNames = ['ops2_1092', 'ops2_1092', 'ops2_1092', 'enigma_1189', 'enigma_1189', 'enigma_1189']
    LFilters = ["u", "y", '',   "u", "y", '']
    LNightMax = [1e4, 1e4, 730, 1e4, 1e4, 730]

    # WIC 2015-12-28 - 23:00 - try using a different SED template,
    # just go with single filters for now
    #
    # DO WE NEED THIS??
    

    # WIC 2015-12-28 - 22:00; much to my surprise, that took less than
    # half an hour to go all the way through. Try again, this time using slightly more filters.    
    runNames = ['ops2_1092', 'enigma_1189', 'ops2_1092', 'enigma_1189']
    LFilters = ['', '', 'griz', 'griz']  # (griz was not recognized)

    # WIC 2015-12-29 - set up for a master-run with all cases, this time with plotting limits
    # Break the specifications across lines to make subdivision easier
    
    # Subsets by time first, then by filter, finally the whole shebang
    
    # (Yes the inversion of the first two is deliberate.)
    runNames = ['enigma_1189', 'ops2_1092', 'ops2_1092', 'enigma_1189', \
                    'ops2_1092', 'enigma_1189', 'ops2_1092', 'enigma_1189', \
                    'ops2_1092', 'enigma_1189']
    LFilters = ['', '', '', '', \
                    'u', 'u', 'y', 'y', \
                    '', '']  
    LNightMax = [365, 365, 730, 730, \
                     1e4, 1e4, 1e4, 1e4, \
                     1e4, 1e4]

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


    print "runAstrom.go INFO - will run the following:"
    for iSho in range(len(runNames)):
        print "%i: %-12s, %1s, %i" % (iSho, runNames[iSho], LFilters[iSho], LNightMax[iSho])
    print "==========================="

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

        # All spatial maps use percentile clipping
        for plotMetric in DPlotArgs.keys():
            DPlotArgs[plotMetric][0].defaultPlotDict['percentileClip'] = SpatialClip

        # Some limits common to spatial maps and histograms
        for iPl in range(0,2):
            DPlotArgs['propmotion'][iPl].defaultPlotDict['logScale'] = True
            
        # Standardized range for the histograms for new parallax metrics
        DPlotArgs['coverage'][1].defaultPlotDict['xMin'] = 0.
        DPlotArgs['coverage'][1].defaultPlotDict['xMax'] = 1.
        DPlotArgs['HAdegen'][1].defaultPlotDict['xMin'] = -1.
        DPlotArgs['HAdegen'][1].defaultPlotDict['xMax'] =  1.
            
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
    seeingCol = 'finSeeing'

    # Try it out for a 20th mag star with a flat SED (can change mag
    # or to OBAFGKM)
    # rmag = 20. ## NOW AN ARGUMENT
    #SedTemplate='flat'

    # Use all the observations. Can change if you want a different
    # time span
    sqlconstraint = ''

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
        outDir = '%s_nside%i_%s_n%i_r%s' % (run, nside, ThisFilter, ThisNightMax, sMag)

        # Ensure we'll be able to find this later on...
        if CustomPlotLimits:
            outDir = '%s_lims' % (outDir)

        # From this point onwards, stuff actually gets run. This is
        # the place to output what will actually happen next.
        print "runAstrom.go INFO - about to run:"
        print "runAstrom.go INFO - sqlconstraint: %s ; run name %s ; nside %i" % (sqlconstraint, run, nside)
        print "runAstrom.go INFO - output directory will be %s" % (outDir)
        if not DoRun:
            continue

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

        metric = metrics.ParallaxCoverageMetric(rmag=rmag, seeingCol=seeingCol, SedTemplate=SedTemplate)
        bundle = metricBundles.MetricBundle(metric, slicer, sqlconstraint, runName=run,
#                                            plotFuncs=plotFuncs, \
                                                plotFuncs=plotFuncsCoverage, \
                                                summaryMetrics=summaryMetrics)
        bundleList.append(bundle)

        metric = metrics.ParallaxHADegenMetric(rmag=rmag, seeingCol=seeingCol, SedTemplate=SedTemplate)
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

#
# repolotAstromMetrics.py 
#

#
# Replots astrometry metrics using plot options set here
#

import os, copy
import glob


import matplotlib.pyplot as plt
import lsst.sims.maf.metricBundles as metricBundles

# Example calls:

#replotAstromMetrics.runFound(metric='properMotion', plotDictIn={'binsize':0.05, 'logScale':True})


# replotAstromMetrics.runFound(metric='parallax', plotDictIn={'binsize':0.05, 'logScale':False})

# replotAstromMetrics.runFound(metric='parallax', plotDictIn={'binsize':0.05, 'logScale':False}, sFilter='u')

# replotAstromMetrics.runFound(metric='parallax', plotDictIn={'binsize':0.05, 'logScale':False}, sFilter='y')



def runFound(dirTop='metricEvals', metric='properMotion', \
                 sFilter='griz', \
                 plotDictIn={'binsize':0.05, 'logScale':True} \
                 #plotDictIn={'bins':2000, 'logScale':True} \
                 ):

    """Run a set of plots for proper motion"""

    # Some limits dictionaries:
    xLims = {}
    xLims['properMotion'] = [25, 10, 3 ]
    xLims['parallax'] = [10, 10, 2]

    if len(sFilter) < 2:
        xLims['parallax'][-1] = 10.
        xLims['properMotion'][-1] = 4.

    units = {}
    units['properMotion'] = 'mas/yr'
    units['parallax'] = 'mas'

    # which key do we lookup?
    sLookup = 'properMotion'
    if metric in xLims.keys():
        sLookup = metric[:]

    # direcs
    LDirs = glob.glob('%s/*_%s_*21p0*lims' % (dirTop, sFilter))

    for sDir in LDirs:
        
        # how many days?
        nDays = sDir.split('nside')[-1].split(sFilter)[-1].split('_')[1].split('n')[-1]
        nDays = int(nDays)

        # ok now set this programmatically
        if nDays < 400:
            iLim = 0
        if 400 < nDays <= 800:
            iLim = 1
        if nDays > 800:
            iLim = 2

        plotDictThis = copy.deepcopy(plotDictIn)
        plotDictThis['xMax'] = xLims[sLookup][iLim]
        
        newUnits = ''
        if metric in units.keys():
            newUnits = units[metric]
        
        if nDays < 400:
            plotDictThis['binsize'] *= 2

        go(sDir, metric, plotDict=plotDictThis, units=newUnits)


def go(dirIn='', metric='properMotion', dirOut='testReplot', \
           plotDict = {}, units=''):

    """Replots a particular metric"""

    # on my system the defailt path is long - set it here.
    if len(dirIn) < 1:
        dirIn = 'metricEvals/astro_lsst_01_1004_nside64_griz_n365_r21p0_lims'

    if len(dirOut) < 1:
        dirOut = os.getcwd()

    if not os.access(dirOut, os.R_OK):
        os.mkdir(dirOut)

    if not os.access(dirIn, os.R_OK):
        print "replotAstromMetrics.go FATAL - cannot read inpath %s" \
            % (dirIn)
        return 

    # find .npz files for this metric
    LEval = glob.glob('%s/*%s*.npz' % (dirIn, metric))
                      
    if len(LEval) < 1:
        print "replotAstromMetrics.go FATAL - no %s .npz present in %s" \
            & (metric, dirIn)
        return 

    pathEval = LEval[0][:]

    print pathEval

    # close pre-existing figures
    plt.close("all")

    # now load this up
    mb = metricBundles.createEmptyMetricBundle()
    mb.read(pathEval)

    # set the plot dicts appropriately
    #for sArg in plotDict.keys():
    #    mb.plotDict[sArg] = plotDict[sArg]

    #print mb.plotDict

    mb.setPlotDict(plotDict)

    # set the units
    if len(mb.metric.units) < 1:
        mb.metric.units = units[:]


    DFigs = mb.plot(savefig=False)
    

    # now save the figures somewhere we can control
    sFigStem = pathEval.split('/')[-1].split('.')[0]

    # construct the filenames
    for sKey in ['SkyMap', 'Histogram']:
        if not sKey in DFigs.keys():
            continue

        sOut = '%s/%s_%s.png' % (dirOut, sFigStem, sKey)

        thisFig = plt.figure(DFigs[sKey])

        if os.access(sOut, os.R_OK):
            os.remove(sOut)
        thisFig.savefig(sOut)

    #print "Figure num:", dum

    
    

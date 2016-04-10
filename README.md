# lsstScratchWIC

Notebooks, random calculations along the way to LSST figures of merit.

**2016-04-10** Updated with consistent paths; the notebooks should now 
all work 'out of the box.' By default, the notebooks look in subdirectory
data/metricOutputs for metrics to load and combine (if you uncomment the
relevant lines in those notebooks). 

There is also an output directory data/fomOutputs - however I recommend you 
test somewhere else first before making that your output directory since 
it's part of the repository.

**2016-03-29** Repository started with notebooks and routines written in 
late Jan 2015 in order to produce the strawman "Galactic Supernova" 
figure of merit.

This is an example of a FoM where the pre-computed metric (over all the 
sky) can be multiplied by another metric, and summed to produce the FoM 
desired.

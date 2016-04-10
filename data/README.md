# README #

WIC 2016-04-10: Various supporting data for figures of merit.

There is a subdirectory 'fomOutputs' to capture output that you want to send up to the repository. Generally you probably 
don't want to use this for output while testing.

Currently the runs of the individual metrics (SN2010mc-like supernova transient, and Mike Lund's "density" metric) are 
stored in the subdirectory "metricRuns" . The notebook that then reads both metrics will need to know where these are 
stored.

I have not corrected the paths in the notebooks to reflect this github repository, you'll have to do that in the notebook. 
(Would be a very welcome contribution!!)

**Note:** The original opsim runs used are not included here since they are large. For the runs here, I used:

* enigma1189   --  Baseline cadence as of 2015
 
* ops2_1092  -- PanSTARRS-like cadence with decent plane coverage.

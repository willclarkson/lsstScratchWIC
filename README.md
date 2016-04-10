# lsstScratchWIC

Notebooks, random calculations along the way to LSST figures of merit.

The notebooks should now all work "out of the box," once the paths to
precomputed metrics are set (if you are using precomputed metrics).

### Data and paths ###

By default, the notebooks all look in subdirectories of the working
directory for the precomputed metrics. 

However, if you uncomment the relevant lines in the notebooks, they
will look in subdirectory data/metricOutputs in the repository. This
is handy if you want other users to be able to use your pre-computed
metrics, or if you want to replicate someone else's shared work before
extending it to your own use-case.

There is also an output directory data/fomOutputs - however I recommend you
test somewhere else first before making that your output directory since
it's part of the repository.

### Handling the OpSim runs ###

* The OpSim database files are large (typically 4.4G per run) so it's probably not a good idea to include them in the repository.

* When running, I have been putting a symlink to the opsim run into the
working directory. Something lke the following:

ops2_1092_sqlite.db -> /Users/clarkson/Data/LSST/OpSimRuns/Runs_20151229/LocalCopies/ops2_1092_sqlite.db

* However this is messy. You can also set variable "opsimDir" in the
  notebooks to point to the location you stored the opsim _sqlite.db
  files on your system. It should be obvious from each notebook where
  that happens, ask me (WIC) if not!

* Within the notebook, the syntax to input the opsim choice into the
metric looks like the following: 

runName1092 = 'ops2_1092' 

opsdb1092 = db.OpsimDatabase(runName1092 + '_sqlite.db')

(Note that runName1092 gets sent to the metric object, and it is the
string in brackets that sets the input path).

* The opsim runs can be found here:

[http://lsst.org/scientists/simulations/opsim/opsim-v332-benchmark-surveys]

### Suggested sequence if running from scratch ###

1. **cd ./My/Test/Directory**

2. Copy the two notebooks below into this working directory. Then run
them. 

3. **TransientTest_CompareWithPanSTARRS-LikeSN2010mc.ipynb** -- computes the
"transient" metric, for the two OpSim runs 1189 and 1092.

4. **FigureOfMerit_4p3_Galactic_Supernova.ipynb** -- computes the density
metric for 1189 and 1092, then reads them back in (along with the
transient metrics) to compute the figure of merit.

### History ###

**2016-04-10:** Updated with consistent paths, and the precomputed metrics
for the "Galactic Supernova" case have been added to the data/metricOutputs
subdirectory. 

**2016-03-29** Repository started with notebooks and routines written in 
late Jan 2015 in order to produce the strawman "Galactic Supernova" 
figure of merit.

This is an example of a FoM where the pre-computed metric (over all the 
sky) can be multiplied by another metric, and summed to produce the FoM 
desired.

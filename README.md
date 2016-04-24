# lsstScratchWIC

Notebooks and calculations along the way to LSST figures of
merit. **Installation instructions that worked on my system, for
sims_maf (confluence version), sims_maf_contrib, and the github
version of sims_maf are in Sections 6 & 7 below of this README.**

I make no claims that all these routines will work on your system!
This is mostly a collection of routines and steps that worked for
me. This should allow you to get up and running with metrics and
figures of merit reasonably quickly.

I acknowledge Peter Yoachim for his help and considerable patience
with my queries, as well as Keaton Bell for suggesting the version.py
workaround below.

### 1. Reminder/warning - changes in OpSim runs since 2015 ###

~~The notebooks should now all work "out of the box," once the paths
to precomputed metrics are set (if you are using precomputed
metrics).~~ **Update 2016-04-11:** OpSim runs from 2016 January
onwards have different column definitions, and MAF has been updated to
follow the new convention - which is not backwards compatible. The
routines in **python/** and **notebooks/** in this repository should
work with the 2016-era OpSim and sims_maf.

Some of the notebooks and python for the pre-2016 versions are in
subdirectories **python/legacy/** and **notebooks/legacy/**. If you
have a version of MAF before about December 2015, and the older OpSim
runs listed below, those all *should* still work OK. Even if you are
using 2016-era MAF, I *think* the notebook
**./notebooks/legacy/FigureOfMerit_4p3_Galactic_Supernova.ipynb**
should still work if you use pre-computed metrics rather than
rerunning the metrics (i.e. set topDir and skip past the subsection
running the metrics). 

For the baseline and PanSTARRS-like surveys respectively, below is the
name-change (for more, including small changes to column definitions, see http://lsst.org/scientists/simulations/opsim/opsim-v335-benchmark-surveys):
* Baseline strategy: **enigma_1189** --> **minion_1016**
* PanSTARRS-like: **ops2_1092** --> **minion_1020**

**If you want to run the metrics that go into the figure of merit, you
will also need to have sims_maf and maf_contrib installed on your
system.** Instructions for installing both are provided a little lower
down in this README (Sections 6 & 7).

### 2. Data and paths ###

By default, the notebooks all look in subdirectories of the working
directory for the precomputed metrics. Outputs are also by default
sent into subdirectories of the working directory.

However, if you uncomment the relevant lines in the notebooks, they
will look in subdirectory data/metricOutputs in the repository. This
is handy if you want other users to be able to use your pre-computed
metrics, or if you want to replicate someone else's shared work before
extending it to your own use-case.

This repository does have an output directory data/fomOutputs in which
Figure-of-Meric outputs might go. However I recommend you test
somewhere else first before making that your output directory since
it's part of the repository.

### 3. Handling the OpSim runs ###

* The OpSim database files are large (typically 4.4G per run) so it's probably not a good idea to include them in this repository (updating would take a long time!).

* When running, I have been putting a symlink to the opsim run into the
working directory. Something lke the following:

ops2_1092_sqlite.db -> /Users/clarkson/Data/LSST/OpSimRuns/Runs_20151229/LocalCopies/ops2_1092_sqlite.db

* However this is messy. You can also set variable "opsimDir" in the
  notebooks to point to the location you stored the opsim _sqlite.db
  files on your system. It should be obvious from each notebook where
  that happens, ask me (WIC) if not!

* Within the notebook, the syntax to input the opsim choice into the
metric and then send the output into some preferred location, looks
like the following:

runNamePSlike = 'minion_1020'

opsdbPSlike = db.OpsimDatabase(opsimDir + '/' + runNamePSlike + '_sqlite.db')

outDirPSlike = '%s/TransientsLike2010mc_PSlike' % (outDir)

resultsDbPSlike = db.ResultsDb(outDir=outDirPSlike)

(Note that **runNamePSlike** gets sent to the metric object, and it is the
string in brackets when defining **opsdbPSlike** that sets the input path).

### 4. Where to get the OpSim runs ###

* The **OLD** opsim runs can be found here... http://lsst.org/scientists/simulations/opsim/opsim-v332-benchmark-surveys

* **... however you almost certainly want the new ones, with which the
  current version of sims-maf is compatible:**

http://lsst.org/scientists/simulations/opsim/opsim-v335-benchmark-surveys

### 5. Suggested sequence if running from scratch ###

(The specific examples are for 2015-era OpSim runs, but the principle is the same for 2016.)

1. **cd ./My/Test/Directory**

2. Copy the two notebooks below into this working directory. Then run
them. 

3. **TransientTest_CompareWithPanSTARRS-LikeSN2010mc.ipynb** -- computes the
"transient" metric, for the two OpSim runs 1189 and 1092.

4. **FigureOfMerit_4p3_Galactic_Supernova.ipynb** -- computes the density
metric for 1189 and 1092, then reads them back in (along with the
transient metrics) to compute the figure of merit.

### 6. HOWTO install sims-maf and maf_contrib, and get them working ###

Here are the steps that worked on my system (2016-04-11, OS X
Yosemite). I did the binary install using anaconda's "conda" package
management environment. This still required updating my PATH (at the
end of this section) but otherwise was reasonably smooth.

If you are not using anaconda python, your installation steps will differ. In that case I recommend going to the following link for
lsst-sims: https://confluence.lsstcorp.org/display/SIM/Catalogs+and+MAF

Note that there might be special difficulties with El Captan, I
haven't tried on that OS yet. The following steps are in the official
install instructions linked to above. In order:

**6.1. Installing lsst-sims or lsst-sims-maf**

* conda config --add channels http://eupsforge.net/conda/dev

* conda install lsst-sims-maf

* Now locate the **eups-setups.csh** file (or .sh if on bash). It
  should be in the bin/ subdirectory of your anaconda installation. On
  my system this was located at
  /Applications/anaconda/bin/eups-setups.csh .

* source /Applications/anaconda/bin/eups-setups.csh

* setup sims_maf

**6.2. Installing maf_contrib**

* Navigate your browser to
  https://github.com/LSST-nonproject/sims_maf_contrib and take a look
  at the contents.

* git clone git@github.com:LSST-nonproject/sims_maf_contrib.git

* cd sims_maf_contrib

* If you haven't already: source /Applications/anaconda/bin/eups-setups.csh

* eups declare -r . -t $USER 
  * Apparently only needs to be done once on install. When running later, you won't need to do this again.

* setup sims_maf_contrib -t $USER -t sims

**6.3. Setting the PATH**

On my system, importing lsst.sims.maf failed because anaconda python
was not in the PATH on my system. I had to put the following at the
end of my ~/.tcshrc file:

* setenv PATH /Applications/anaconda/bin:${PATH}

**6.4. Running sims_maf and maf_contrib**

* cd to some test directory on your system.

* cp -p /path/to/maf_contrib/tutorials/Getting_MAF_Help.ipynb

* Either run the following commands one by one, or put them into a
  shell script that you can call at your convenience:
  * source /Applications/anaconda/bin/eups-setups.csh
  * setup sims_maf
  * setup sims_maf_contrib -t $USER -t sims

* Now try the notebook:
  * jupyter notebook Getting_MAF_Help.ipynb

**6.5. jupyter notebook vs ipython notebook**

On my system, trying to run ipython notebook resulted in a deprecation warning and a delayed launch. Jupyter seems to be preferred. To install it:
* conda install jupyter

If your PATH includes your anaconda installation, then that should be all you need to run jupyter from the command line.

### 7. HOWTO get the github version of sims_maf working on your system ###

**WIC 2016-04-24:** For some reason conda is not upating sims_maf past
version 2.0.1.5 on my system, and version sims_2.2.4 is needed to
apply certain parallax metrics on the 2016 runs. I therefore needed to
use the github version of sims_maf. 

Since that failed to work out of the box on my system - but there is a
workaround - I provide the steps here in case they are useful to
you. In order:

* Navigate your browser to https://github.com/LSST-nonproject/sims_maf_contrib
  * (Probably a good idea to fork if you think you will be contributing pull requests)

* cd /path/to/my/github/clones

* git clone the repository

* cd ./sims_maf

* eups declare sims_maf git -r .

* eups declare sims_maf git -t $USER

To test, in a new shell try:

* source ~/anaconda/bin/eups-setups.csh (or your equivalent)

* setup sims_maf -t $USER

* In your ipython shell or notebook: 
  * from lsst.sims.maf.metrics import calibrationMetrics

On my system this initially failed, because **version.py** was missing
from the github version. ("No module named version" in the error
message.) The canonical way to fix this:

* cd /path/to/my/github/clones/sims_maf/

* scons
  * or ~/anaconda/bin/scons if you don't have scons in your path

* ls /path/to/my/github/clones/sims_maf/sst/sims/maf/version.py

If the above steps produce no **version.py** in that location, the
import will probably fail again. On my system, **scons** failed
outright.

There is a workaround, which was suggested to me by Keaton Bell: copy
a pre-built **version.py** into the required location. While the version
information will be incorrect, at least the github version of sims_maf
will run on your system! A canned **version.py** file is included in this
repository, in the subdirectory miscRequiredFiles/   . So:

* cd /path/to/my/github/clones/sims_maf/sst/sims/maf

* cp -p /path/to/my/github/clones/lsstScratchWIC/miscRequiredFiles/version.py .

At this point, the import should work fine. Try testing again in a new shell:

* source ~/anaconda/bin/eups-setups.csh (or your equivalent)

* setup sims_maf -t $USER

* In your ipython shell or notebook: 
  * from lsst.sims.maf.metrics import calibrationMetrics

... and all should be well.


### 8. History ###

(Only changes major enough for a comment are included!)

**2016-04-24:** Added runAstrom.py for the astrometry metrics in WP
  chapter 4 for 2016, and a dummy version.py that I needed to get the
  github version of sims_maf working on my system. README updated.

**2016-04-10:** Updated with consistent paths, and the precomputed metrics
for the "Galactic Supernova" case have been added to the data/metricOutputs
subdirectory. 

**2016-03-29** Repository started with notebooks and routines written in 
late Jan 2015 in order to produce the strawman "Galactic Supernova" 
figure of merit.

This is an example of a FoM where the pre-computed metric (over all the 
sky) can be multiplied by another metric, and summed to produce the FoM 
desired.

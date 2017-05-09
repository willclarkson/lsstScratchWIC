# lsstScratchWIC

Notebooks and calculations along the way to LSST figures of merit. 
*Installation instructions that worked on my system, for sims_maf 
(confluence version), and the github version of sims_maf are in Sections 
6 & 7 below of this README. The instructions for sims_maf_contrib worked 
on my system until about two weeks ago, they should work on your 
system.*

This repository is entirely unofficial and is not connected to the LSST 
sims_maf and maf_contrib repositories.

I make no claims that all these routines will work on your system!
This is mostly a collection of routines and steps that worked for
me. This should allow you to get up and running with metrics and
figures of merit reasonably quickly.

I thank Peter Yoachim for his help and considerable patience with my 
queries, as well as Keaton Bell for suggesting the version.py workaround 
below (update 2017-05-08 that workaround no longer needed, but was vital when I 
had to use it!!).

~~**2016-04-24 Update:** I am finding **sims_maf_contrib** no longer 
functions on my system, although there is a workaround (in Section 6.2 
below). Hopefully this will be fixed soon.~~ **2017-05-08** Fixed; 
maf_contrib installs and runs fine.

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
"transient" metric, for the Baseline and PanSTARRS-like OpSim runs.

4. **FigureOfMerit_4p3_Galactic_Supernova.ipynb** -- computes the
density metric for Baseline and PanSTARRS strategies, then reads them
back in (along with the transient metrics) to compute the figure of
merit.

### 6. HOWTO install sims-maf and maf_contrib, and get them working ###

**2017-04-28 Update** - the binary version of sims_maf is apparently
  somewhat out of date; now building from source is recommended. I
  have moved the old installation steps (for 2016) to the file
  **installSteps2016.md** in this directory. So far I have
  successfully installed sims_maf and maf_contrib on Mac Yosemite (OS
  X 10.10.5) and Ubuntu Linux (16.04), although in both cases there
  were additional steps I had to run. Those are listed below.

Here are links to installation instructions from the project.

LSST stack using newinstall.sh (required):
(https://pipelines.lsst.io/install/newinstall.html)

LSST sims_maf (building from source recommended):
(https://confluence.lsstcorp.org/display/SIM/Catalogs+and+MAF)

sims_maf_contrib:
(https://github.com/LSST-nonproject/sims_maf_contrib)

Below are the commands I typed, in order, to install on the two
systems to which I currently have access (OS X 10.10.5 and Ubuntu
16.0.4).

**6.1. Preparing for the installation (Ubuntu 16.04.2 LTS)**

Two packages on my Ubuntu system caused build errors: fftw3 and
libgcc. The fftw3 problem broke the build from source in step 6.2
below. The libgcc problem was more subtle - while the software built
all the way through to the end, I got import errors when actually
trying to run one of the analysis notebooks. Here are the steps I took
to solve the problems:

To install fftw3 in shared mode:
* cd ~/Soft/
* Download from [http://www.fftw.org/download.html](http://www.fftw.org/download.html);
    * wget (http://www.fftw.org/fftw-3.3.6-pl2.tar.gz)    
* To install in "shared mode" (see also (http://micro.stanford.edu/wiki/Install_FFTW3#Build_and_Install)):
    * gunzip fftw-3.3.6-pl2.tar.gz
    * tar -xvf fftw-3.3.6-pl2.tar
    * cd fftw-3.3.6-pl2
    * ./configure --enable-shared=yes --mpi=yes
    * make 
    * sudo make install

To get round the glibcc problem that occurred later on:
* conda install libgcc

**6.2. Building lsst stack from source** ([LSST instructions](https://pipelines.lsst.io/install/newinstall.html)):

* mkdir ~/Soft/lsst

* cd ~/Soft/lsst

* unset LSST_HOME EUPS_PATH LSST_DEVEL EUPS_PKGROOT REPOSITORY_PATH

* curl -OL https://raw.githubusercontent.com/lsst/lsst/13.0/scripts/newinstall.sh
* source ./loadLSST.csh

    * (Answer "yes" when prompted if you want to install miniconda)

* eups distrib install lsst_apps  
    * (installs 93 items, takes about three hours)

**6.3 Preparing for and building sims_maf** ([confluence link with instructions](https://confluence.lsstcorp.org/display/SIM/Catalogs+and+MAF#CatalogsandMAF-installation)):

**On OS X Yosemite (10.10.5):** Due to an astropy issue, on my OS X system the first attempt to build sims_maf failed. The second step below is the workaround to fix this. See [this issue for more.](https://community.lsst.org/t/sims-utils-2-3-4-sims-eupspkg-build-from-source-fails-os-x-10-10-5/1820)

* setup lsst_distrib  

* **On OS X Yosemite (10.10.5):** change log_to_file=False in file ~/.astropy/astropy.cfg (not any of the other astropy_*.cfg variants in that directory)

* eups distrib install lsst_sims -t sims
   * Installs 88 items, takes about 90 minutes. The astropy file issue I was finding, hits at item 58/88 (sims_utils 2.3.4.sims)

**6.4 Installing maf_contrib:** ([maf_contrib instructions](https://github.com/LSST-nonproject/sims_maf_contrib)):

* (If in a new terminal:) source ~/Soft/lsst/loadLSST.csh 
    * loadLSST.bash if you're using bash, similar for other shells

~~* (If in a new terminal:) setup lsst_distrib~~

* (If in a new terminal:) setup sims_maf -t sims

* cd ~/Soft

* git clone https://github.com/LSST-nonproject/sims_maf_contrib.git

* cd sims_maf_contrib

* eups declare sims_maf_contrib -r . -t $USER
    * This throws a warning that the path is absolute, not relative. I think this can be safely ignored.

**6.5. Running sims_maf and maf_contrib**

(Assuming this is all from a new terminal):

* cd to some test directory on your system.

* (example notebookt to test:) cp -p /path/to/maf_contrib/tutorials/Getting_MAF_Help.ipynb .

* Either run the following commands one by one, or put them into a
  shell script that you can call at your convenience:
  * source ~/Soft/lsst/loadLSST.csh
  * setup sims_maf -t sims
  * setup sims_maf_contrib -t $USER -t sims

* Now try the notebook:
  * jupyter notebook Getting_MAF_Help.ipynb

**6.6. jupyter notebook vs ipython notebook**

On my system, trying to run ipython notebook resulted in a deprecation warning and a delayed launch. Jupyter seems to be preferred. To install it:
* conda install jupyter

If your PATH includes your anaconda installation, then that should be all you need to run jupyter from the command line.

### 7. HOWTO get the github version of sims_maf working on your system ###

**WIC 2017-04-28** - the issue below seems to have been fixed in the
  new maf version. I have copied the suggestions below to
  **installSteps2016.md **. For completeness, the issue is below.

**WIC 2016-04-24:** For some reason conda is not upating sims_maf past
version 2.0.1.5 on my system, and version sims_2.2.4 is needed to
apply certain parallax metrics on the 2016 runs. I therefore needed to
use the github version of sims_maf. 

### 8. History ###

(Only changes major enough for a comment are included!)

**2017-04-28:** Rewrote the installation instructions in the Readme to
  reflect the updated sims_maf. Old instructions moved to
  **installSteps2016.md**

**2016-04-25:** Added **shellScripts** subdirectory. Scripts useful to 
organise the output of several runs can be found there.

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

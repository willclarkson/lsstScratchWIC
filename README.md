# lsstScratchWIC

Notebooks, random calculations along the way to LSST figures of merit.

~~The notebooks should now all work "out of the box," once the paths
to precomputed metrics are set (if you are using precomputed
metrics).~~ **Update 2016-04-11:** OpSim runs from 2016 January
onwards have different column definitions, and MAF has been updated to
follow the new convention. This breaks backwards compatibility, which
means the material here will not work with MAF installed after about
Dec 2015 or with 2016's OpSim runs. I will have to update the
notebooks in this repository to follow the new convention.

For the moment, however, if you have a version of MAF before about
December 2015, and the older OpSim runs listed below, this all
*should* still work OK. 

Even if you are using 2016-era MAF, I *think* the notebook
FigureOfMerit_4p3_Galactic_Supernova.ipynb should still work if you
use pre-computed metrics rather than rerunning the metrics (i.e. set
topDir and skip past the subsection running the metrics).

### sims_maf and maf_contrib ###

If you want to run the metrics that go into the figure of merit, you
will also need to have sims_maf and maf_contrib installed on your
system. Instructions for installing both are provided a little lower
down in this README.

### Data and paths ###

By default, the notebooks all look in subdirectories of the working
directory for the precomputed metrics. Outputs are also by default
sent into subdirectories of the working directory.

However, if you uncomment the relevant lines in the notebooks, they
will look in subdirectory data/metricOutputs in the repository. This
is handy if you want other users to be able to use your pre-computed
metrics, or if you want to replicate someone else's shared work before
extending it to your own use-case.

There is also an output directory data/fomOutputs - however I recommend you
test somewhere else first before making that your output directory since
it's part of the repository.

### Handling the OpSim runs ###

* The OpSim database files are large (typically 4.4G per run) so it's probably not a good idea to include them in this repository (updating would take a long time!).

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

### HOWTO install sims-maf and maf_contrib, and get them working ###

Here are the steps that worked on my system (2016-04-11, OS X
Yosemite). I did the binary install using anaconda's "conda" package
management environment. This still required updating my PATH (at the
end of this section) but otherwise was reasonably smooth.

If you are not using anaconda python, your installation steps will differ. In that case I recommend going to the following link for
lsst-sims: https://confluence.lsstcorp.org/display/SIM/Catalogs+and+MAF

Note that there might be special difficulties with El Captan, I
haven't tried on that OS yet. The following steps are in the official
install instructions linked to above. In order:

**1. lsst-sims**

* conda config --add channels http://eupsforge.net/conda/dev

* conda install lsst-sims
  * (Could also conda install lsst-sims-maf - however the full lsst-sims has Galsim included, which may prove useful).

* Now locate the **eups-setups.csh** file (or .sh if on bash). It
  should be in the bin/ subdirectory of your anaconda installation. On
  my system this was located at
  /Applications/anaconda/bin/eups-setups.csh .

* source /Applications/anaconda/bin/eups-setups.csh

* setup sims_maf

**2. maf_contrib**

* Navigate your browser to
  https://github.com/LSST-nonproject/sims_maf_contrib and take a look
  at the contents.

* git clone git@github.com:LSST-nonproject/sims_maf_contrib.git

* cd sims_maf_contrib

* If you haven't already: source /Applications/anaconda/bin/eups-setups.csh

* eups declare -r . -t $USER 
  * Apparently only needs to be done once on install. When running later, you won't need to do this again.

* setup sims_maf_contrib -t $USER -t sims

**3. Setting the PATH**

On my system, importing lsst.sims.maf failed because anaconda python
was not in the PATH on my system. I had to put the following at the
end of my ~/.tcshrc file:

* setenv PATH /Applications/anaconda/bin:${PATH}

**4. Running sims_maf and maf_contrib**

* cd to some test directory on your system.

* cp -p /path/to/maf_contrib/tutorials/Getting_MAF_Help.ipynb

* Either run the following commands one by one, or put them into a
  shell script that you can call at your convenience:
  * source /Applications/anaconda/bin/eups-setups.csh
  * setup sims_maf
  * setup sims_maf_contrib -t $USER -t sims

* Now try the notebook:
  * jupyter notebook Getting_MAF_Help.ipynb

**5. jupyter notebook vs ipython notebook**

On my system, trying to run ipython notebook resulted in a deprecation warning and a delayed launch. Jupyter seems to be preferred. To install it:
* conda install jupyter

If your PATH includes your anaconda installation, then that should be all you need to run jupyter from the command line.

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

# Old installation steps #

**WIC 2017-04-28:** These are the installation steps that worked in
  2016, but have since been superseded. 

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
  * **UPDATE 2016-04-24** - this step now no longer works on my system (the "sims" tag is invalid). I suspect I am seeing some eups-related problems on this computer. However it should work for you!
  * Workaround: You can still use the modules in sims_maf_contrib by copying the directory into your working directory. (Adding to your $PATH probably also works, but I have not yet tested this. I am hoping to get sims_maf_contrib working again properly without having to mess with the path.)
    * For example, in the FigureOfMerit notebook for the Galactic Supernova, I copied the Starcounts/ directory from sims_maf_contrib into the working directory for the notebook, and was able to use it.  


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

### 7. HOWTO get the github version of sims_maf working on your system ###

**WIC 2017-04-28** - the issue below seems to have been fixed in the new
  maf version. I have copied the suggestions below to **installSteps2016.md **.

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


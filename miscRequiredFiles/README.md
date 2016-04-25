# miscRequiredFiles #

**Created 2016-04-24** (WIC): Store files that might be needed for 
installation on your system. Some notes:

###version.py###

On import, the github version of sims_maf checks for a **version.py** file 
in its **lsst/sims/maf/** directory. If that file is absent, the import 
fails, which was preventing me from running the github version of 
sims_maf at all.

Apparently the **version.py** is created by **scons** during the installation 
process of sims_maf, but that step fails on my system. **The version.py** 
file in this directory is an example kindly supplied by Keaton Bell. I 
have found that copying this file into the directory

/path/to/sims_maf/github/version/sims_maf/python/lsst/sims/maf/

allows the github version of **sims_maf** to import and run. 

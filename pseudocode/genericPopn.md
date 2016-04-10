## genericPopn.md ##

WIC 2016-04-04 - Pseudocode for a generic figure of merit that might
be run to recover complicated population X on the sky, from OpSim run
Z.

**Motivation:** In discussion, it seems clear that FoM's like random
  and systematic error on derived astrophysical (population)
  parameters are likely to be most persuasively conveyed as the output
  of some kind of Monte Carlo for the FoM, with the various
  complications and choices depending on the science case.

This example is for recovery of some population where the main
dependence (for a given sightline) is on apparent magnitude in each
filter. The end-user might have their own preferred mechanism to
simulate populations that they want to plug in.

### Generic Population X recovery ###

* m_g = np.arange(15,32,2)   ; similar for other filters

* Evaluate Photometric error as a vector metric as a function of apparent magnitude in each filter.

* Ditto for other observational quantities of interest (e.g. crowding systematic error, proper motion precision).

* foreach HEALPIX:
  * foreach metric M:
    * Fit the run of M against apparent magnitude in all filters
* Store the results somewhere, call this "Bigarray".

*Now the simulation can proceed using your favorite population simulation, e.g.:*

* Initialise array of "recovered" paramters. Call this "paramRecov"

* for iTrial in range(nMonteCarloTrials):
  * Produce realization of your favorite fake population in Galactic coords
  * translate to (RA, DEC, distance modulus, apparent mag, [other properties])
  * Use Bigarray to assign the measurement uncertainties to this realization
  * evaluate astrophysical parameter of interest
  * paramRecov[iTrial] = copy(thisRecov)

* Store the whole run of recovered minus input parameters - should be a single number or couple of numbers per trial

* Evaluate the entire set suitably to produce the single-number Figure of Merit.

* Repeat the above for example OpSim runs (with and without good plane coverage). Fill in the comparison in the relevant Table in the LSST Whitepaper. 


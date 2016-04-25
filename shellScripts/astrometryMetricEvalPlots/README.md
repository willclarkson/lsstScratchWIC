
#astrometryMetricEvalPlots#

**2016-04-25 (WIC)**: shell scripts used to make Figures 4.2-4.9 in the 
"Astrometry" section of the "Milky Way" chapter within the LSST MW 
Whitepaper.

These all use imagemagick (aliased to "convert" on my system) to 
downsample outputs from runAstrom.py, and to enforce a slightly less 
unwieldy naming convention on the resulting files. Pretty much the 
sequence of commands for one figure, replicated and altered for each of 
the other figures.

I ran this from a subdirectory "GatheredFigures" within the main 
directory within which the metric outputs were stored.

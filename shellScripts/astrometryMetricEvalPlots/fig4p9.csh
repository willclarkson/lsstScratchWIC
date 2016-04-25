#!/bin/tcsh

# For replication: conversion commands to produce downsampled plots
# for Astrometry chapter.
#
#

# Figure 4.9 on page 87

# Spatial maps

convert -resize 50% ../minion_1016_nside64_y_n10000_r21p0_lims/thumb.minion_1016_parallax_y_and_night_lt_10000_HEAL_SkyMap.png ./MW_Astrom_paError_Baseline_y_map.png
convert -resize 50% ../minion_1016_nside64_u_n10000_r21p0_lims/thumb.minion_1016_parallax_u_and_night_lt_10000_HEAL_SkyMap.png ./MW_Astrom_paError_Baseline_u_map.png
convert -resize 50% ../minion_1016_nside64_ugrizy_n10000_r21p0_lims/thumb.minion_1016_parallax_night_lt_10000_HEAL_SkyMap.png ./MW_Astrom_paError_Baseline_10y_map.png

convert -resize 50% ../minion_1020_nside64_ugrizy_n10000_r21p0_lims/thumb.minion_1020_parallax_night_lt_10000_HEAL_SkyMap.png ./MW_Astrom_paError_PanSTARRS_10y_map.png
convert -resize 50% ../minion_1020_nside64_u_n10000_r21p0_lims/thumb.minion_1020_parallax_u_and_night_lt_10000_HEAL_SkyMap.png ./MW_Astrom_paError_PanSTARRS_u_map.png
convert -resize 50% ../minion_1020_nside64_y_n10000_r21p0_lims/thumb.minion_1020_parallax_y_and_night_lt_10000_HEAL_SkyMap.png ./MW_Astrom_paError_PanSTARRS_y_map.png

# Histograms

convert -resize 50% ../minion_1016_nside64_y_n10000_r21p0_lims/thumb.minion_1016_parallax_y_and_night_lt_10000_HEAL_Histogram.png ./MW_Astrom_paError_Baseline_y_hst.png
convert -resize 50% ../minion_1016_nside64_u_n10000_r21p0_lims/thumb.minion_1016_parallax_u_and_night_lt_10000_HEAL_Histogram.png ./MW_Astrom_paError_Baseline_u_hst.png
convert -resize 50% ../minion_1016_nside64_ugrizy_n10000_r21p0_lims/thumb.minion_1016_parallax_night_lt_10000_HEAL_Histogram.png ./MW_Astrom_paError_Baseline_10y_hst.png
convert -resize 50% ../minion_1020_nside64_ugrizy_n10000_r21p0_lims/thumb.minion_1020_parallax_night_lt_10000_HEAL_Histogram.png ./MW_Astrom_paError_PanSTARRS_10y_hst.png
convert -resize 50% ../minion_1020_nside64_u_n10000_r21p0_lims/thumb.minion_1020_parallax_u_and_night_lt_10000_HEAL_Histogram.png ./MW_Astrom_paError_PanSTARRS_u_hst.png
convert -resize 50% ../minion_1020_nside64_y_n10000_r21p0_lims/thumb.minion_1020_parallax_y_and_night_lt_10000_HEAL_Histogram.png ./MW_Astrom_paError_PanSTARRS_y_hst.png

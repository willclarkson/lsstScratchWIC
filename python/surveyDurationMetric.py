# ======================================================================
# Will Clarkson (willclarkson) <wiclarks@umich.edu>
# ======================================================================

# WIC 2016-05-24

# Used Lynne Jones' "Writing A New Metric.ipynb" as an example. Some of
# Lynne's tutorial comments are kept in here so that I can understand
# how to make additions later.

# Import BaseMetric, or have it available to inherit from
from lsst.sims.maf.metrics import BaseMetric

import numpy as np

# Define our class, inheriting from BaseMetric
class PercentileRangeMetric(BaseMetric):

    """
    Calculate the total duration (in days) of survey coverage in the
    slice. Argument 22 is a percentile (to be used if you want to
    avoid being fooled by one or two very early or very late
    exposures).

    Inputs with default values:
    ---------------------------
         colname    (default 'expJD')
    
         percentile (default 100.): Upper or lower percentile to use. 

    Note that the percentages used for the interval are
    symmetric. This means that the same range is returned if
    percentile=10. as if percentile=90. Both will return the duration
    in days between the 10th and 90th percentile of the time values. 

    """

    # Add our "__init__" method to instantiate the class.  We will
    # make the 'percentile' value an additional value to be set by the
    # user.  **kwargs allows additional values to be passed to the
    # BaseMetric that you may not have been using here and don't want
    # to bother with.
    def __init__(self, colname='expMJD', percentile=100., **kwargs):

        # Set the values we want to keep for our class.
        self.colname = colname
        self.percentile = percentile

        # Now we have to call the BaseMetric's __init__ method, to get
        # the "framework" part set up.  We currently do this using
        # 'super', which just calls BaseMetric's method.  The call to
        # super just basically looks like this .. you must pass the
        # columns you need, and the kwargs.
        super(PercentileRangeMetric, self).__init__(col=colname, **kwargs)
        


    # Now write out "run" method, the part that does the metric calculation.
    def run(self, dataSlice, slicePoint=None):


        # Do some parsing of the inputs, to guarantee 0 <= low <= high <= 100.
        pctHi = np.min([100., self.percentile])
        pctLo = np.max([0., 100.-self.percentile])
        pctArr = np.sort([pctLo, pctHi]) 
    
        # Find the latest minus earliest date in days
        firstLast = np.percentile(dataSlice[self.colname], pctArr)
        return np.max(firstLast) - np.min(firstLast)



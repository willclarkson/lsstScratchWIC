from lsst.sims.maf.metrics import BaseMetric
import numpy as np
from mafContrib import starcount 

# Copy of Mike Lund's CountMetric.py, with slightly tweaked
# syntax to query RA, DEC

class AsCountMetric(BaseMetric):

    """Copy of Mike Lund's CountMetric, but pulling the RA and DEC a
    bit differently"""
    
    def __init__(self,**kwargs):
        
        self.D1=kwargs.pop('D1', 100)
        self.D2=kwargs.pop('D2', 1000)
        super(AsCountMetric, self).__init__(col=[], **kwargs)
        
    def run(self, dataSlice, slicePoint=None):
        sliceRA = np.degrees(slicePoint['ra'])
        sliceDEC = np.degrees(slicePoint['dec'])
        return starcount.starcount(sliceRA, sliceDEC, self.D1, self.D2)

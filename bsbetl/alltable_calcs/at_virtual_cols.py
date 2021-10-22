''' all-table virtual column related code '''

from bsbetl.alltable_calcs import at_Virtual_MovingAverage, at_columns
from numpy.core.numeric import NaN
import pandas as pd


class Virtual_Column(object):

    def __init__(self):
        self.kind = 'Non specialized virtual_column'
        self.name = 'Unnamed virtual column creator'
        self.assoc_columns = []
        self.added_columns = []
        self.added_columns_affinities = {
        }
        self.description = ''

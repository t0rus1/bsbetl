from datetime import datetime
import logging
from numpy.core.numeric import NaN
import pandas as pd
from pandas.core.indexes.base import Index


class Calculation(object):
    """
    Base class that each alltable calculation must inherit from. 
    Here are defined the methods that all at_calculations must implement
    """

    def __init__(self, name):
        self.name = name
        self.description = 'not provided'
        self.dependents = []
        self.at_computeds = []
        self.ov_computeds = []
        logging.info(f'{self.name} initialized...')

    # def prepare_columns(self, df: pd.DataFrame, initValue=NaN):
    #     """ This method our consumer should call 
    #     after construction to get needed columns added to the dataframe
    #     """
    #     # add the columns we'll be deriving
    #     for col in self.at_computeds:
    #         if not col in df.columns:
    #             df[col] = initValue

    #     return self  # allows for chaining

    def calculate(df: pd.DataFrame, share_num: str, dates_in_df: list, top_up: bool, stage: int):
        """This is the method, if implemented, that our framework can call to get the entire date range computed
        """
        raise NotImplementedError

    def day_calculate(df: pd.DataFrame, share_num: str, row_idx: Index, top_up: bool, stage: int):
        """This is the method, if implemented, that our framework can call to get a single date computed
        """
        raise NotImplementedError


''' all-table virtual column related code '''

import pandas as pd
from bsbetl.alltable_calcs import at_columns
from numpy.core.numeric import NaN
from bsbetl.alltable_calcs.at_virtual_cols import Virtual_Column


class at_virtual_DayOfWeek(Virtual_Column):
    """ represents and can creates a column in an all-table dataframe containing moving average price  """

    def __init__(self):
        super().__init__()
        self.kind = 'All-table virtual column'
        self.name = 'DayOfWeek'
        self.assoc_columns = []
        self.added_columns = ['DOW', ]
        self.added_columns_affinities = {
            'DOW': [],
        }
        self.description = 'Day of Week'

    def create_virtual_columns(self, df_arg: pd.DataFrame, parameters: list) -> pd.DataFrame:
        """The actual implementation of the plugin 
        """
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

        df_arg['DOW'] = pd.to_datetime(df_arg['date_time']).dt.dayofweek
        df_arg['DOW'] = df_arg['DOW'].apply(lambda x: days[x])

        return df_arg

    def contribute_dash_dropdown_options(stage: int) -> list:

        options_list = []
        options_list.append(
            {'label': 'Day of Week', 'value': 'DOW', 'title': 'insert a temporary day of week column'})
        return options_list

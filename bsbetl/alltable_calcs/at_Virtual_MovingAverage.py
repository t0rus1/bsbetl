''' all-table virtual column related code '''

import pandas as pd
from bsbetl.alltable_calcs import at_columns
from bsbetl.alltable_calcs.at_virtual_cols import Virtual_Column


class at_virtual_MovingAverage(Virtual_Column):
    """ represents and can creates a column in an all-table dataframe containing moving average price  """

    def __init__(self):
        super().__init__()
        self.kind = 'All-table virtual column'
        self.name = 'MovingAveragesPrice'
        self.assoc_columns = ['price']
        self.added_columns = ['MA-5', 'MA-20', 'MA-200']
        self.added_columns_affinities = {
            'MA-5': at_columns.PRICE_AFFINITY,
            'MA-20': at_columns.PRICE_AFFINITY,
            'MA-200': at_columns.PRICE_AFFINITY
        }
        self.description = 'Moving Average Prices'

    def create_virtual_columns(self, df_arg: pd.DataFrame, parameters: list) -> pd.DataFrame:
        """The actual implementation of the plugin 
        """

        #df = argument.loc[argument['Lazy'] == False, :]
        #periods = parameters[0]

        # add a moving average column(s)
        for ma in parameters:
            if ma == self.added_columns[0]:
                df_arg[ma] = df_arg['price'].rolling(window=5).mean()
            if ma == self.added_columns[1]:
                df_arg[ma] = df_arg['price'].rolling(window=20).mean()
            if ma == self.added_columns[2]:
                df_arg[ma] = df_arg['price'].rolling(window=200).mean()

        # print(df_arg.head(15))

        return df_arg

    def contribute_dash_dropdown_options(stage: int) -> list:

        options_list = []

        # price moving averages
        options_list.append(
            {'label': 'MA-5', 'value': 'MA-5', 'title': 'insert a temporary 5 period moving-average price column'})
        options_list.append(
            {'label': 'MA-20', 'value': 'MA-20', 'title': 'insert a temporary 20 period moving-average price column'})
        options_list.append(
            {'label': 'MA-200', 'value': 'MA-200', 'title': 'insert a temporary 200 period moving-average price column'})

        return options_list

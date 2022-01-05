import pandas as pd
import alpaca_trade_api as tradeapi
from config import *

class StockData:
    def __init__(self, symbol, timeframe) -> None:
        self.symbol = symbol
        api = tradeapi.REST(
                    key_id=key_id,
                    secret_key=secret_key,
                    base_url=base_url
        )
        df = api.get_barset(self.symbol, 'day', limit=timeframe).df
        self.df = df[self.symbol]
    
    def get_df(self):
        return self.df

    def delta(self, col):
        df_copy = self.df.copy()
        df_copy['delta_'+col] = self.df[col] - self.df[col].shift(1)
        df_copy.loc[df_copy.index[0], 'delta_'+col]=0
        df_copy['delta_'+col+'_pct'] = round((self.df[col] - self.df[col].shift(1))/self.df[col].shift(1)*100,2)
        df_copy.loc[df_copy.index[0], 'delta_'+col+'_pct']=0
        self.df = df_copy
        return self
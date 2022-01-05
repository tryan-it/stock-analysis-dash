import pandas as pd
from itertools import combinations_with_replacement
from itertools import permutations
import alpaca_trade_api as tradeapi
from config import *

class StockCorr:
    def __init__(self, symbols, timeframe) -> None:
        self.symbols = symbols
        api = tradeapi.REST(
                    key_id=key_id,
                    secret_key=secret_key,
                    base_url=base_url
        )
        self.df = api.get_barset(symbols, 'day', limit=timeframe).df

        self.close = pd.DataFrame()
        for symbol in self.symbols:
            self.close[symbol] = self.df[(symbol,'close')]

    def diff(self, x, y):
        return [i for i in x + y if i not in x or i not in y]

    def get_redundant_pairs(self):
        pairs = self.diff(list(permutations(self.close.columns, 2)),
                         list(combinations_with_replacement(self.close.columns, 2)))
        return pairs

    def get_top_abs_correlations(self, n=5):
        corr = self.close.corr().abs().unstack()
        labels_to_drop = self.get_redundant_pairs()
        corr = corr.drop(labels_to_drop).sort_values(ascending=False)
        self.df = corr[0:n].to_frame()
        self.df = self.df.reset_index()
        self.df.columns = ['Stock A', 'Stock B', 'Corr']
        return self

    def get_df(self):
        return self.df
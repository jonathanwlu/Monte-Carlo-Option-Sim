import path_sampling
import bs
import math
import os
import numpy as np
import pandas as pd


class CallPutTable:
    def __init__(self, length, vol, start, times, strike):
        self.length, self.vol, self.start, self.times, self.strike, self.df = length, vol, start, times, strike, None
        self.make_table()

    def make_table(self):
        print('running norm')
        index = np.linspace(round(self.strike * .7), round(self.strike * 1.3), num=round((self.strike * 1.3 - self.strike * .7) / 10))
        index = np.insert(index, np.searchsorted(index, self.strike), self.strike)
        df = pd.DataFrame(index=index, columns=['Call Price', 'Put Price', 'Call IV', 'Put IV', 'C-P+X-$', 'Avg RV', 'RV SD'])
        df.index.name = 'Strike'
        for i in index:
            print('Strike: ' + str(i))
            print('Vol: ' + str(self.vol))
            call_price, put_price = path_sampling.call_price(self.length, self.vol, self.start, self.times, i), path_sampling.put_price(
                self.length, self.vol, self.start, self.times, i)
            df.loc[i, :] = np.insert(path_sampling.all_including_rv(self.length, self.vol, self.start, self.times, i),
                                  2, [bs.bs_option_implied_vol('c', self.start, i, self.vol, 0, self.length, call_price),
                                      bs.bs_option_implied_vol('p', self.start, i, self.vol, 0, self.length, put_price),
                                      call_price - put_price + self.strike - self.start])
        self.df = df
        return df

    @staticmethod
    def get_index(strike):
        """
        Parameters
        ----------
        strike : float
            Price to center strike prices around

        Returns
        -------
        numpy.ndarray
            Index of table centered around strike as array
        """
        ind = np.linspace(round(strike * .7), round(strike * 1.3),
                          num=round((strike * 1.3 - strike * .7) / 10))
        return np.insert(ind, np.searchsorted(ind, strike), strike)

    def get_table(self):
        """
        Returns
        -------
        pandas.DataFrame
            Copy of table
        """
        return self.df.copy()

    def export_to_csv(self):
        """
        Exports table as csv into montecarlo/out
        """
        print('exporting to call_put_table.csv')
        self.df.to_csv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                    'out', 'call_put_table.csv'))

#!/usr/bin/env python

"""
    File name: strike_table.py
    Author: Jon Lu
    Date created: 6/14/2017
    Date last modified: 6/19/2017
    Python Version: 3.6.1
"""

import path_sampling
import bs
import multiprocessing as mp
import os
import numpy as np
import pandas as pd


class CallPutTable:
    """
    Table consisting of call price, put price, call IV, put IV, call - put + strike - start price, average RV,
    RV standard deviation from simulated results at different strike prices (+/- ~30% of given strike price)

    Attributes
    ----------
    length : int
        Length of simulation in days
    vol : float
        Volatility or standard deviation, annualized, has no effect for 'bootstrap' (refactor later)
    start : float
        Starting, or current, security price
    times : int
        Number of simulations to run for each strike price
    strikes : array-like
        Strike prices to calculate with
    dist : str
        Type of distribution used in ['normal', 'uniform', 'bootstrap', 'double-bell', 'skewnorm'], defaults to 'normal'
        'bootstrap' indicates randomly sampling with replacement from historical log-returns (kwargs['bs_data'])
        'double-bell' indicates distribution from adding two bell curves with means +/- kwargs['delta'] and std devs sqrt((vol ** 2) / 2)
        'double-bell' std dev derived from var(x + y) = var(x) + var(y) for independent random variables
        'skew_a' : skewness parameter for skewnorm dist
    **kwargs
        Keyword arguments, includes:
        'delta' : mean used for normal curves underpinning double bell distribution
        'bs_data' : filename in montecarlo folder of historical data used for bootstrap as csv
        'jumps' : random dist-based "jumps" at different DTEs, represented by dict with keys (dte, dist, mean, sd, delta)
    """

    def __init__(self, length, vol, start, times, strikes, dist='normal', **kwargs):
        self.length, self.vol, self.start, self.times, self.index, self.dist, self.kwargs, self.df = length, vol, start, times, strikes, dist, kwargs, None
        self.make_table()

    def row(self, i):
        """
        For internal use only

        Parameters
        ----------
        i : float
            Strike price to get attributes for

        Returns
        -------
        tuple
            Tuple of given strike price and array of format
            ['Call Price', 'Put Price', 'Call IV', 'Put IV', 'Avg RV', 'RV SD'])
        """
        print('starting strike: ' + str(i))
        output = path_sampling.all_including_rv(self.length, self.vol, self.start, self.times, i, self.dist, **self.kwargs)
        ret = (i, np.insert(output, 2,
                            [bs.bs_option_implied_vol('c', self.start, i, self.vol, 0, self.length, output[0]),
                             bs.bs_option_implied_vol('p', self.start, i, self.vol, 0, self.length, output[1])]))
        print('ending strike: ' + str(i))
        return ret

    def make_table(self):
        """
        For internal use only
        Stores table as self.df

        Returns
        -------
        pandas.DataFrame
            Table of strike prices along with attributes for each price
        """
        # print('running multi')
        mp.freeze_support()
        index = self.index
        # print('index - ' + str(index))
        df = pd.DataFrame(index=index,
                          columns=['Call Price', 'Put Price', 'Call IV', 'Put IV', 'C-P+X-$', 'Avg RV', 'RV SD'])
        df.index.name = 'Strike'
        pool = mp.Pool()
        rows = pool.map(self.row, index)
        pool.close()
        pool.join()
        for a in rows:
            df.loc[a[0], :] = np.insert(a[1], 4, a[1][0] - a[1][1] + float(a[0]) - self.start)
        self.df = df
        return df

    @staticmethod
    def get_index(strike, strike_range, num_strike):
        """
        Parameters
        ----------
        strike : float
            Price to center strike prices around
        strike_range : float
            Range to center strike prices around center (e.g. 30 = 70 to 130 for center at 100)
        num_strike : int
            Number of strikes to plot, not counting center

        Returns
        -------
        numpy.ndarray
            Index of table centered around strike as array
        """
        ind = np.arange(round(strike - strike_range), round(strike + strike_range) * 1.001,
                        round(strike_range * 2 / num_strike), dtype=int)
        if strike not in ind:
            ind = np.insert(ind, np.searchsorted(ind, strike), strike)
        return ind

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

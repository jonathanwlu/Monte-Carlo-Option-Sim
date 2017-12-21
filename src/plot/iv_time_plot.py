#!/usr/bin/env python

"""
    File name: iv_time_plot.py
    Author: Jon Lu
    Date created: 6/15/2017
    Date last modified: 6/19/2017
    Python Version: 3.6.1
"""

import path_sampling
import bs
import math
import multiprocessing as mp
import os.path as op
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def avg_or_drop(a, b):
    """
    Parameters
    ----------
    a : float
    b : float

    Returns
    -------
    float
        a if b equals 0 and vice-versa, or avg(a, b) if neither equal 0
    """
    if a == 0:
        return b
    elif b == 0:
        return a
    return np.mean([a, b])


class TimeTable:
    """
    Table consisting of call IV, put IV, average RV from simulated results at different lengths (DTEs/days to end)

    Attributes
    ----------
    lengths : array-like
        List of lengths to plot IV for
    vol : float
        Volatility of underlying security
    start : float
        Starting, or current, security price
    times : int
        Number of simulations to run for each strike price
    strike : float
        Price to center strike prices around
    dist : str
        Type of distribution used in ['normal', 'uniform', 'bootstrap', 'double-bell', 'skewnorm'], defaults to 'normal'
        'double-bell' indicates distribution from adding two bell curves with means +/- kwargs['delta'] and std devs sqrt((vol ** 2) / 2)
        'double-bell' std dev derived from var(x + y) = var(x) + var(y) for independent random variables
    **kwargs
        Keyword arguments, includes:
        'delta' : mean used for normal curves underpinning double bell distribution
        'bs_data' : historical data used for bootstrap (array-like)
        'skew_a' : skewness parameter for skewnorm dist
    """

    def __init__(self, lengths, vol, start, times, strike, dist='normal', **kwargs):
        self.lengths, self.vol, self.start, self.times, self.strike, self.dist, self.kwargs, self.df = lengths, vol, start, times, strike, dist, kwargs, None
        self.make_table()

    def row(self, length):
        """
        For internal use only

        Parameters
        ----------
        length : int
            Path length to get IVs for

        Returns
        -------
        tuple
            Tuple of given length, call IV, put IV, and avg RV
        """
        print('starting length: ' + str(length))
        result = path_sampling.all_including_rv(length, self.vol, self.start, self.times, self.strike, self.dist, **self.kwargs)
        cp = result[0]
        pp = result[1]
        ret = (length, bs.bs_option_implied_vol('c', self.start, self.strike, self.vol, 0, length, cp),
               bs.bs_option_implied_vol('p', self.start, self.strike, self.vol, 0, length, pp), result[2])
        print('ending length: ' + str(length))
        return ret

    def make_table(self):
        """
        For internal use only
        Stores table as self.df
        """
        mp.freeze_support()
        df = pd.DataFrame(index=self.lengths, columns=['Call IV', 'Put IV', 'RV'])
        df.index.name = 'DTE'
        pool = mp.Pool()
        rows = pool.map(self.row, self.lengths)
        pool.close()
        pool.join()
        for a in rows:
            df.loc[a[0], :] = [a[1], a[2], a[3]]
        self.df = df

    def get_table(self):
        """
        Returns
        -------
        pandas.DataFrame
            Table of DTEs along with call and put IVs and avg RV for each DTE
        """
        return self.df


def plot(center_length, length_range, num_lengths, vol, start_price, times, strike, filename=False, dist='normal', **kwargs):
    """
    Parameters
    ----------
    center_length : int
        Center length to plot IV for
    length_range : int
        Range to build lengths array around center_length, e.g. 50 with center_length = 100 would be 50-150
    num_lengths : int
        Number of lengths in range, not including center
    vol : float
        Volatility or standard deviation, annualized, has no effect for 'bootstrap' (refactor later)
    start_price : float
        Starting, or current, security price
    times : int
        Number of simulations to run for each strike price
    strike : float
        Target strike price
    filename : string
        Output file name (with or without .png extension)
        Will always output as .png
        If not specified, will display but not save plot
    dist : str
        Type of distribution used in ['normal', 'uniform', 'bootstrap', 'double-bell', 'skewnorm'], defaults to 'normal'
        'bootstrap' indicates randomly sampling with replacement from historical log-returns (kwargs['bs_data'])
        'double-bell' indicates distribution from adding two bell curves with means +/- kwargs['delta'] and std devs sqrt((vol ** 2) / 2)
        'double-bell' std dev derived from var(x + y) = var(x) + var(y) for independent random variables
    **kwargs
        Keyword arguments, includes:
        'delta' : mean used for normal curves underpinning double bell distribution
        'bs_data' : filename in montecarlo folder of historical data used for bootstrap as csv
        'skew_a' : skewness parameter for skewnorm dist
    """
    if dist == 'bootstrap':
        kw = pd.read_csv(op.join(op.abspath(op.join(__file__, op.pardir, op.pardir, op.pardir)), kwargs['bs_data']), index_col=0).iloc[:, 0]
        pairs = zip(kw[:-1], kw[1:])
        log_returns = [math.log(pair[1] / pair[0]) for pair in pairs]
        vol = np.std(log_returns) * math.sqrt(252)
    lengths = np.arange(center_length - length_range, (center_length + length_range) * 1.001,
                        round(length_range * 2 / num_lengths), dtype=int)
    if center_length not in lengths:
        lengths = np.insert(lengths, np.searchsorted(lengths, center_length), center_length)
    lengths = [x for x in lengths if x > 0]
    t = TimeTable(lengths, vol, start_price, times, strike, dist, **kwargs)
    df = t.get_table()
    v_avg_or_drop = np.vectorize(avg_or_drop)
    res = pd.DataFrame({'Black–Scholes Implied Vol': v_avg_or_drop(df.loc[:, 'Call IV'].values, df.loc[:, 'Put IV'].values),
                        'Average Realized Vol': df.loc[:, 'RV']}, index=df.index)
    res.to_csv(op.join(op.abspath(op.join(__file__, op.pardir, op.pardir, op.pardir)),
                            'out', (filename if filename.lower().endswith('.csv') else filename + '.csv')))
    ax = res.plot(grid=1)
    title_dist_type = dict([('normal', 'Normal'), ('uniform', 'Uniform'), ('bootstrap', 'Bootstrap'),
                            ('double-bell', 'Double Bell'), ('skewnorm', 'Skew-normal')])
    plt.title(str(times) + ' Paths, ' + title_dist_type[dist] + ' Return Dist' +
              ', Vol=' + str(vol) +
              ', Start=' + str(start_price) +
              ', Strike=' + str(strike))
    plt.xlabel('Days to Expiration')
    plt.ylabel('Volatility')
    plt.ylim(-.1, 1 if res.iloc[:, 0].max() > .4 else .5)
    if filename is False:
        plt.show()
    else:
        plt.savefig(op.join(op.abspath(op.join(__file__, op.pardir, op.pardir, op.pardir)),
                            'out', (filename if filename.lower().endswith('.png') else filename + '.png')))


# if __name__ == "__main__":
#     df = pd.read_csv(op.join(op.abspath(op.join(__file__, op.pardir, op.pardir, op.pardir)), 'spec', 'stkPx.csv'))
#     data = df.loc[:, 'AdjClose'].tolist()[:-1]
#     plot(range(10, 70, 10), .25, 97.5, 1000, 100, dist='bootstrap', bs_data=data)
#     plot(range(10, 70, 10), .25, 97.5, 100, 100, dist='normal')

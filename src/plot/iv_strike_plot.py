#!/usr/bin/env python

"""
    File name: iv_strike_plot.py
    Author: Jon Lu
    Date created: 6/14/2017
    Date last modified: 6/19/2017
    Python Version: 3.6.1
"""

import os.path as op
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import strike_table


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


def plot(length, start_price, times, center_strike, strike_range, num_strike, filename=False, dist='normal', **kwargs):
    """
    Parameters
    ----------
    length : int
        Length of simulation in days
    start_price : float
        Starting, or current, security price
    times : int
        Number of simulations to run for each strike price
    center_strike : float
        Price to center strike prices around
    strike_range : float
        Range to center strike prices around center (e.g. 30 = 70 to 130 for center at 100)
    num_strike : int
        Number of strikes to plot, not counting center
    filename : string
        Output file name (with or without .png extension)
        Will always output as .png
        If not specified, will display but not save plot
    dist : str
        Type of distribution used in ['normal', 'uniform', 'bootstrap', 'double-bell', 'skewnorm'], defaults to 'normal'
        'double-bell' indicates distribution from adding two bell curves with means +/- kwargs['delta'] and std devs sqrt((vol ** 2) / 2)
        'double-bell' std dev derived from var(x + y) = var(x) + var(y) for independent random variables
    **kwargs
        Keyword arguments, includes:
        'delta' : mean used for normal curves underpinning double bell distribution
        'bs_data' : filename in montecarlo folder of historical data used for bootstrap as csv
        'jumps' : random dist-based "jumps" at different DTEs, represented by dict with keys (dte, dist, mean, sd, delta)
        'skew_a' : skewness parameter for skewnorm dist
    """
    calls = pd.DataFrame(index=strike_table.CallPutTable.get_index(center_strike, strike_range, num_strike), columns=np.linspace(.15, .35, 9))
    puts = pd.DataFrame(index=strike_table.CallPutTable.get_index(center_strike, strike_range, num_strike), columns=np.linspace(.15, .35, 9))
    for i in np.linspace(.15, .35, 9):
        print('-' * 15)  # separator
        print('starting vol: ' + str(i))
        call_and_put = strike_table.CallPutTable(length, i, start_price, times,
                                                 strike_table.CallPutTable.get_index(center_strike, strike_range, num_strike),
                                                 dist, **kwargs).get_table().loc[:, ['Call IV', 'Put IV']]
        calls.loc[:, i] = call_and_put.loc[:, 'Call IV']
        puts.loc[:, i] = call_and_put.loc[:, 'Put IV']
        print('ending vol: ' + str(i))
        print('-' * 15)  # separator
    v_avg_or_drop = np.vectorize(avg_or_drop)
    df = pd.DataFrame(v_avg_or_drop(calls, puts), index=calls.index, columns=calls.columns)
    df.to_csv(op.join(op.abspath(op.join(__file__, op.pardir, op.pardir, op.pardir)),
                            'out', (filename if filename.lower().endswith('.csv') else filename + '.csv')))
    plt.close('all')
    ax = df.plot(grid=1)
    title_dist_type = dict([('normal', 'Normal'), ('uniform', 'Uniform'), ('bootstrap', 'Bootstrap'),
                            ('double-bell', 'Double Bell'), ('skewnorm', 'Skew-normal')])
    plt.title(str(times) + ' ' + str(length) + 'D Paths, ' + title_dist_type[dist] + ' Return Dist')
    plt.xlabel('Strike Price')
    plt.ylabel('Implied Volatility')
    plt.axvline(x=center_strike)
    ax.legend().set_title('Actual Vol')
    if filename is False:
        plt.show()
    else:
        plt.savefig(op.join(op.abspath(op.join(__file__, op.pardir, op.pardir, op.pardir)),
                            'out', (filename if filename.lower().endswith('.png') else filename + '.png')))

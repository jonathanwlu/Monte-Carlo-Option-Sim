#!/usr/bin/env python

"""
    File name: forward_predictions.py
    Author: Jon Lu
    Date created: 6/15/2017
    Date last modified: 6/15/2017
    Python Version: 3.6.1
"""

import os.path as op
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import path_sampling
import bs


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


def get_table(length, vol, start_price, times):
    """
    Gets table of IV vs days before exp for single option of fixed length, with strike price at the start price,
    with DTE as steps of 10 between 0 and 60 inclusive
    IV-DTE equivalent of iv_strike_plot

    Parameters
    ----------
    length : int
        Length of simulation in days
    vol : float
        Volatility of underlying security
    start_price : float
        Starting, or current, security price
    times : int
        Number of simulations to run for each strike price
    """
    strike_price = start_price
    paths = path_sampling.path(length, vol, start_price, times)
    points = [[path[day] for path in paths] for day in range(-1, -62, -10)]
    call_prices = [np.mean([x - strike_price if x - strike_price > 0 else 0 for x in day]) for day in points]
    put_prices = [np.mean([strike_price - x if strike_price - x > 0 else 0 for x in day]) for day in points]
    call_ivs = [bs.bs_option_implied_vol('c', start_price, strike_price, vol, 0, z[0], z[1]) for z in zip(range(0, 61, 10), call_prices)]
    put_ivs = [bs.bs_option_implied_vol('p', start_price, strike_price, vol, 0, z[0], z[1]) for z in zip(range(0, 61, 10), put_prices)]
    v_avg_or_drop = np.vectorize(avg_or_drop)
    return v_avg_or_drop(call_ivs, put_ivs)


def plot(length, vol, start_price, times, filename=False):
    """
    Parameters
    ----------
    length : int
        Length of simulation in days
    vol : float
        Volatility of underlying security
    start_price : float
        Starting, or current, security price
    times : int
        Number of simulations to run for each strike price
    filename : string
        Output file name (with or without .png extension)
        Will always output as .png
        If not specified, will display but not save plot
    """
    if filename is False:
        plt.show()
    else:
        plt.savefig(op.join(op.abspath(op.join(__file__, op.pardir, op.pardir, op.pardir)),
                            'out', (filename if filename.lower().endswith('.png') else filename + '.png')))

plot(100, .25, 100, 100)

#!/usr/bin/env python

"""
    File name: path_sampling.py
    Author: Jon Lu
    Date created: 6/13/2017
    Date last modified: 6/19/2017
    Python Version: 3.6.1
"""

import math
import ast
import os.path as op
import numpy as np
import scipy.stats
import pandas as pd


def step_sample(last, dist, mean=0.0, sd=1.0, delta=0.0, skew_a=0.0):
    """Only for normal/uniform/double-bell, used for steps and jumps"""
    if dist == 'normal':
        return last * math.exp(np.random.normal(loc=mean, scale=sd) - .5 * sd ** 2)
    elif dist == 'uniform':
        return last * math.exp(np.random.uniform(-sd * math.sqrt(3), sd * math.sqrt(3)) + mean - .5 * sd ** 2)
    elif dist == 'skewnorm':
        return last * math.exp(scipy.stats.skewnorm.rvs(skew_a, mean, sd) + mean - .5 * sd ** 2)
    elif dist == 'double-bell':
        sub_vol = math.sqrt((sd ** 2) / 2)
        return last * math.exp(np.random.normal(loc=-delta + mean, scale=sub_vol) + np.random.normal(loc=delta + mean, scale=sub_vol) - .5 * sd ** 2)


def single_path(length, vol, start, dist, **kwargs):
    """Use path() instead"""
    if dist not in ['normal', 'uniform', 'bootstrap', 'double-bell', 'skewnorm']:
        raise ValueError("""dist must be string in ['normal', 'uniform', 'bootstrap', 'double-bell']""")
    if 'jumps' in kwargs:
        jumps = ast.literal_eval(kwargs['jumps'])
        jump_dtes = [j['dte'] for j in jumps]
    else:
        jump_dtes = []
    vol_d = vol / math.sqrt(252)  # un-annualize
    arr = np.empty(length + 1)
    arr[0] = start
    if dist == 'bootstrap':
        if 'bs_data' not in kwargs:
            raise ValueError("""call with bootstrap must include key 'bs_data' in kwargs""")
        kw = pd.read_csv(op.join(op.abspath(op.join(__file__, op.pardir, op.pardir)), kwargs['bs_data']), index_col=0).iloc[:, 0]
        pairs = zip(kw[:-1], kw[1:])
        log_returns = [math.log(pair[1] / pair[0]) for pair in pairs]
        for i in range(length):
            arr[i + 1] = arr[i] * math.exp(np.random.choice(log_returns) - .5 * vol_d ** 2)
            if length - 2 - i in jump_dtes:  # -2 because i + 1 = 49 is day 50 (b/c range is zero-indexed)
                d = [j for j in jumps if j['dte'] == length - 2 - i][0]
                arr[i + 1] = step_sample(arr[i + 1], d['dist'], d['mean'], d['sd'] / math.sqrt(252), d['delta'])
        return arr
    else:
        delta = 0
        skew_a = 0
        if dist == 'double-bell':
            if 'delta' not in kwargs:
                raise ValueError("""call with double-bell distribution must include key 'delta' in kwargs""")
            delta = float(kwargs['delta'])
        if dist == 'skewnorm':
            if 'skew_a' not in kwargs:
                raise ValueError("""call with skewnorm distribution must include key 'skew_a' in kwargs""")
            skew_a = float(kwargs['skew_a'])
        for i in range(length):
            arr[i + 1] = step_sample(arr[i], dist, sd=vol_d, delta=delta, skew_a=skew_a)
            if length - 2 - i in jump_dtes:
                d = [j for j in jumps if j['dte'] == length - 2 - i][0]
                arr[i + 1] = step_sample(arr[i + 1], d['dist'], d['mean'], d['sd'] / math.sqrt(252), d['delta'], d['skew_a'])
        return arr


def path(length, vol, start, times, dist, **kwargs):
    """

    Parameters
    ----------
    length : int
        Length of path, excluding start
    vol : float
        Volatility or standard deviation, annualized, has no effect for 'bootstrap' (refactor later)
    start : float
        Start position
    times : int
        Number of paths to create
    dist : str
        Type of distribution used in ['normal', 'uniform', 'bootstrap', 'double-bell', 'skewnorm'], defaults to 'normal'
        'bootstrap' indicates randomly sampling with replacement from historical log-returns (kwargs['bs_data'])
        'double-bell' indicates distribution from adding two bell curves with means +/- kwargs['delta'] and std devs sqrt((vol ** 2) / 2)
        'double-bell' std dev derived from var(x + y) = var(x) + var(y) for independent random variables
    **kwargs
        Keyword arguments, includes:
        'delta' : mean used for normal curves underpinning double bell distribution
        'bs_data' : filename in montecarlo folder of historical data used for bootstrap as csv
        'jumps' : random dist-based "jumps" at different DTEs, represented by dict with keys (dte, dist, mean, sd, delta)
        'skew_a' : skewness parameter for skewnorm dist

    Returns
    -------
    numpy.ndarray
        Array of each step of path (including start), or array of such arrays

    """
    if times <= 0 or times % 1 != 0:
        raise ValueError('times must be integer > 0!')
    elif times == 1:
        return single_path(length, vol, start, dist, **kwargs)
    else:
        return np.array([single_path(length, vol, start, dist, **kwargs) for _ in range(times)])


def ends(length, vol, start, times, dist, **kwargs):
    """

    Returns
    -------
    numpy.ndarray
        Array of last step of each path

    """
    return np.array([i[-1] for i in path(length, vol, start, times, dist, **kwargs)])


def call_price(length, vol, start, times, strike, dist, **kwargs):
    """

    Parameters
    ----------
    strike : float
        Strike price of option

    Returns
    -------
    float
        Call price of option

    """
    return np.mean([x - strike if x - strike > 0 else 0 for x in ends(length, vol, start, times, dist, **kwargs)])


def put_price(length, vol, start, times, strike, dist, **kwargs):
    """

    Returns
    -------
    float
        Put price of option

    """
    return np.mean([strike - x if strike - x > 0 else 0 for x in ends(length, vol, start, times, dist, **kwargs)])


def rv(paths):
    """

    Parameters
    ----------
    paths : numpy.ndarray or list
        List of paths to calculate from (use path() to generate list)

    Returns
    -------
    numpy.ndarray
        RV of individual paths

    """
    return np.array(
        [math.sqrt(np.mean([np.log(path[i + 1] / path[i]) ** 2 for i in range(path.size - 1)]) * 252) for path in
         paths])


def all_including_rv(length, vol, start, times, strike, dist, **kwargs):
    """

    Returns
    -------
    numpy.ndarray
        Call price, put price, avg RV, RV sd from one set of paths

    """
    paths = path(length, vol, start, times, dist, **kwargs)
    ends = np.array([i[-1] for i in paths])
    rvs = rv(paths)
    return np.array([
        np.mean([x - strike if x - strike > 0 else 0 for x in ends]),
        np.mean([strike - x if strike - x > 0 else 0 for x in ends]),
        np.mean(rvs),
        np.std(rvs)
    ])

#!/usr/bin/env python

"""
    File name: bs.py
    Author: Jon Lu
    Date created: 6/13/2017
    Date last modified: 6/13/2017
    Python Version: 3.6.1
"""

import math
from scipy.stats import norm

DAYS_IN_YEAR = 365.25  # average days per year
TDAYS_IN_YEAR = 252  # trading days per year


def bs_option_price(option_type, stock_price,
                    strike, vol, interest,
                    days_to_exp, is_td=True):
    """ Return theoretical option price
    Does not raise exceptions (per request), invalid parameters may still return result!

    Parameters
    ----------
    option_type : str
        Call or put
    stock_price : float
        Current stock price
    strike : float
        Strike price
    vol : float
        BS Volatility
    interest : float
        Interest rate
    days_to_exp : int
        Days until option expiration
    is_td : bool or int
        Whether to calculate using trading days (optional, default value is True)

    Returns
    -------
    float
        Black-Scholes theoretical option price

    """
    if days_to_exp <= 0 or vol <= 0:
        if option_type[0].casefold() == 'c':
            if strike > stock_price:
                return 0.0
            return stock_price - strike
        if strike < stock_price:
            return 0.0
        return strike - stock_price
    else:
        if not is_td:
            t = days_to_exp / DAYS_IN_YEAR
        else:
            t = days_to_exp / TDAYS_IN_YEAR
        vol2 = vol * math.sqrt(t)
        h = (math.log(stock_price / strike) + (interest + .5 * vol ** 2) * t) / vol2
        h2 = h - vol2
        if option_type[0].casefold() == 'c':
            return stock_price * norm.cdf(h) - strike * math.exp(-interest * t) * norm.cdf(h2)
        return -stock_price * norm.cdf(-h) + strike * math.exp(-interest * t) * norm.cdf(-h2)


def bs_option_delta(option_type, stock_price,
                    strike, vol, interest,
                    days_to_exp, is_td=True):
    """Return price derivative by stock price
    Does not raise exceptions (per request), invalid parameters may still return result!

    Parameters
    ----------
    option_type : str
        Call or put
    stock_price : float
        Current stock price
    strike : float
        Strike price
    vol : float
        BS Volatility
    interest : float
        Interest rate
    days_to_exp : int
        Days until option expiration
    is_td : bool or int
        Whether to calculate using trading days (optional, default value is True)

    Returns
    -------
    float
        Black-Scholes delta

    """
    if option_type[0].casefold() == 's':
        return 1.0
    elif days_to_exp <= 0 or vol <= 0.000000001 or strike <= 0:
        if option_type[0].casefold() == 'c':
            if strike >= stock_price:
                return 0.0
            return 1.0
        if strike <= stock_price:
            return 0.0
        return -1.0
    else:
        if not is_td:
            t = days_to_exp / DAYS_IN_YEAR
        else:
            t = days_to_exp / TDAYS_IN_YEAR
        vol2 = vol * math.sqrt(t)
        h = (math.log(stock_price / strike) + (interest + .5 * vol ** 2) * t) / vol2
        h2 = h - vol2
        if option_type[0].casefold() == 'c':
            return norm.cdf(h)
        return -norm.cdf(-h)


def bs_option_gamma(option_type, stock_price,
                    strike, vol, interest,
                    days_to_exp, is_td=True):
    """Return second derivative by stock price
    Does not raise exceptions (per request), invalid parameters may still return result!

    Parameters
    ----------
    option_type : str
        Call or put
    stock_price : float
        Current stock price
    strike : float
        Strike price
    vol : float
        BS Volatility
    interest : float
        Interest rate
    days_to_exp : int
        Days until option expiration
    is_td : bool or int
        Whether to calculate using trading days (optional, default value is True)

    Returns
    -------
    float
        Black-Scholes gamma

    """
    if days_to_exp <= 0 or vol <= 0:
        return 0
    if not is_td:
        t = days_to_exp / DAYS_IN_YEAR
    else:
        t = days_to_exp / TDAYS_IN_YEAR
    vol2 = vol * math.sqrt(t)
    h = (math.log(stock_price / strike) + (interest + .5 * vol ** 2) * t) / vol2
    return norm.pdf(h) / stock_price / vol2


def bs_option_vega(option_type, stock_price,
                    strike, vol, interest,
                    days_to_exp, is_td=True):
    """Return derivative of volatility to option price
    Does not raise exceptions (per request), invalid parameters may still return result!

    Parameters
    ----------
    option_type : str
        Call or put
    stock_price : float
        Current stock price
    strike : float
        Strike price
    vol : float
        BS Volatility
    interest : float
        Interest rate
    days_to_exp : int
        Days until option expiration
    is_td : bool or int
        Whether to calculate using trading days (optional, default value is True)

    Returns
    -------
    float
        Black-Scholes vega

    """
    if days_to_exp <= 0 or vol <= 0:
        return 0
    if not is_td:
        t = days_to_exp / DAYS_IN_YEAR
    else:
        t = days_to_exp / TDAYS_IN_YEAR
    vol2 = vol * math.sqrt(t)
    h = (math.log(stock_price / strike) + (interest + .5 * vol ** 2) * t) / vol2
    return norm.pdf(h) * stock_price * vol2 / vol / 100


def bs_option_rho(option_type, stock_price,
                    strike, vol, interest,
                    days_to_exp, is_td=True):
    """Return derivative of time to option price
    Does not raise exceptions (per request), invalid parameters may still return result!

    Parameters
    ----------
    option_type : str
        Call or put
    stock_price : float
        Current stock price
    strike : float
        Strike price
    vol : float
        BS Volatility
    interest : float
        Interest rate
    days_to_exp : int
        Days until option expiration
    is_td : bool or int
        Whether to calculate using trading days (optional, default value is True)

    Returns
    -------
    float
        Black-Scholes rho

    """
    if days_to_exp <= 0 or vol <= 0:
        return 0
    if not is_td:
        t = days_to_exp / DAYS_IN_YEAR
    else:
        t = days_to_exp / TDAYS_IN_YEAR
    vol2 = vol * math.sqrt(t)
    h = (math.log(stock_price / strike) + (interest + .5 * vol ** 2) * t) / vol2
    h2 = h - vol2
    if option_type[0].casefold() == 'c':
        return (norm.pdf(h) - strike / stock_price * math.exp(-interest * t)
                * norm.pdf(h2) * stock_price * math.sqrt(t) / vol
                + strike * t * math.exp(-interest * t) * norm.cdf(h2))
    return (norm.pdf(-h) - strike / stock_price * math.exp(-interest * t)
            * norm.pdf(-h2) * stock_price * math.sqrt(t) / vol
            - strike * t * math.exp(-interest * t) * norm.cdf(-h2))


def bs_option_implied_vol(option_type, stock_price,
                    strike, vol, interest,
                    days_to_exp, option_price, is_td=True):
    """Implied BS volatility
    Does not raise exceptions (per request), invalid parameters may still return result!

    Parameters
    ----------
    option_type : str
        Call or put
    stock_price : float
        Current stock price
    strike : float
        Strike price
    vol : float
        BS Volatility
    interest : float
        Interest rate
    days_to_exp : int
        Days until option expiration
    option_price : float
        Price of option
    is_td : bool or int
        Whether to calculate using trading days (optional, default value is True)

    Returns
    -------
    float
        Implied BS vol

    """
    # If the option is below parity, iv = 0
    if (not days_to_exp
        or (option_type[0].casefold() == 'c'
            and option_price < stock_price - strike)
        or (option_type[0].casefold() == 'p'
            and option_price < strike - stock_price)):
        return 0.0
    p0 = -1000
    v = 0
    for i in range(3):
        if abs(option_price - p0) <= .01:
            break
        v = vol * (1 + .625 * i)
        vega = 100 * bs_option_vega(option_type, stock_price,
                                    strike, v, interest,
                                    days_to_exp, is_td)
        if abs(vega) < .00001 and vol < 1000:
            v = 10 * vol
        p = option_price
        for _ in range(10):
            p0 = p
            p = bs_option_price(option_type, stock_price,
                                strike, v, interest,
                                days_to_exp, is_td)
            vega = 100 * bs_option_vega(option_type, stock_price,
                                        strike, v, interest,
                                        days_to_exp, is_td)
            if abs(vega > .00001) and abs(p - p0) > .000001:
                v += (option_price - p) / vega
            else:
                break
    return v

from handles import *
from stats import basic_stats
from pprint import pprint
from datetime import datetime
from scipy.stats import norm
import numpy as np
from math import sqrt, floor
import os
from dates import *

def pdiv(a, b):
    if b == 0:
        return 0
    return a/b



def bs_call(S, K, T, r, v, cr=1):
    d1 = np.log(S/(K/(1 + r)**T)/(v*sqrt(T))) + (v*sqrt(T))/2
    d2 = d1 - v * np.sqrt(T)
    bs =  S * norm.cdf(d1) - (K/(1 + r)**T) * norm.cdf(d2)
    return bs * cr

def bs_put(S, K, T, r, v, cr=1):
    d1 = (np.log(S/K) + (r + v**2/2)*T) / (v*np.sqrt(T)) 
    d2 = d1 - v* np.sqrt(T)
    bs = (K/(1 + r)**T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    return bs * cr

def trend(option):

    f = list(option.values())
    if f[9] < f[12]:
        o = f[12]
    else:
        o = f[9] * 1.05
    return pdiv(f[0], o)

def x_load(option, bar, exp):
    '''
    0  : adjusted_mark_price
    1  : ask_price
    2  : ask_size
    3  : bid_price
    4  : bid_size
    5  : break_even_price
    6  : high_price
    7  : last_trade_price
    8  : last_trade_size
    9  : low_price
    10 : mark_price
    11 : open_interest
    12 : previous_close_price
    13 : volume
    14 : chance_of_profit_long
    15 : chance_of_profit_short
    16 : delta
    17 : gamma
    18 : implied_volatility
    19 : rho
    20 : theta
    21 : vega
    22 : high_fill_rate_buy_price
    23 : high_fill_rate_sell_price
    24 : low_fill_rate_buy_price
    25 : low_fill_rate_sell_price
    26 : type
    27 : strike_price
    '''
    v, o, c, h, l = bar
    f = list(option.values())

    if f[26] == 1:
        bs = bs_call(c, f[27], exp, 0, f[18]+.001)
    else:
        bs = bs_put(c, f[27], exp, 0, f[18]+.001)

    option_trend                = pdiv(f[0], f[12])
    stock_trend                 = pdiv(c, o) 
    spread                      = pdiv(f[1], f[3])
    volume_interest_ratio       = pdiv(f[11], f[13])
    option_stock_trend_ratio    = pdiv(option_trend, stock_trend)
    until_break_even_percentage = pdiv(f[5], c) 
    until_strike_percentage     = pdiv(f[27], c)
    black_scholes_price_ratio   = pdiv(f[0], bs)
    low_high_spred              = pdiv(f[6], f[9])
    chance_profit_long          = f[14]
    chance_profit_short         = f[15]
    volume                      = f[13]
    volatility                  = f[18]
    delta, gamma, rho, theta, vega = f[16], f[17], f[19], f[20], f[21]

    x = [
        option_trend, stock_trend, spread,
        volume_interest_ratio, option_stock_trend_ratio,
        until_break_even_percentage, until_strike_percentage,
        black_scholes_price_ratio,
        chance_profit_long, chance_profit_short,
        delta, gamma, rho, theta, vega,
        volatility, 
    ]
    return x

def scan(option, constraints):
    for a, o, v in constraints:
        if o == '=':
            if option[a] != v:
                return False
        if o == '>':
            if option[a] < v:
                return False
        if o == '<':
            if option[a] > v:
                return False
    return True

def rolling_xy(w, d1, d2, exp, constraints):
    X, y, ids = [], [], []

    bars = read_json(f'data/{w}/{d1}/bars.json')
    options = read_json(f'data/{w}/{d1}/{exp}.json')
    future = read_json(f'data/{w}/{d2}/{exp}.json')

    until_exp = time_until_exp(exp, d1)
    id_map = {}

    for sym, chains in options.items():
        bar = bars[sym]
        id_map.update(future[sym])
        for _id, option in chains.items():
            if scan(option, constraints):
                x = x_load(option, bar, until_exp)
                ids.append(_id)
                X.append(x)
    for _id in ids:
        y.append(trend(id_map[_id]))
    return X, y

def load_train(weeks, exp_level, constraints=[]):
    X, y = [], []

    for w in weeks:
        dates = sorted(os.listdir(f'data/{w}'))
        exp = sorted(os.listdir(f'data/{w}/{dates[0]}/'))[exp_level][:-5]
        for d1, d2 in zip(dates, dates[1:]):
            _x, _y = rolling_xy(w, d1, d2, exp, constraints)
            X.extend(_x)
            y.extend(_y)

    return np.array(X), np.array(y)

def backtest(model, weeks, exp_level, constraints=[], port_size=10):
    returns = {}
    for w in weeks:
        dates = sorted(os.listdir(f'data/{w}'))
        exp = sorted(os.listdir(f'data/{w}/{dates[0]}/'))[exp_level]
        for d1, d2 in zip(dates, dates[1:]):
            X, y = rolling_xy(w, d1, d2, exp, constraints)
            y_pred = model.predict(X)
            top = sorted(zip(y, y_pred), key=lambda x: x[1], reverse=True)[:port_size]
            returns[d2] = round(np.mean([x[0] for x in top]), 5)
    array_returns = list(returns.values())
    returns_stats = basic_stats(array_returns)
    return returns, returns_stats

if __name__ == '__main__':
    exp_level = 2
    train_weeks    = ['2021-04-12_2021-04-16']
    backtest_dates = ['2021-04-15', '2021-04-16']
    constraints = [
        ('type', '=', 1),
        ('adjusted_mark_price', '>', .05),
    ]

    X, y = load_train(train_weeks, exp_level, constraints=constraints)
    print(X.shape)
    print(y.shape)



from robin_stocks import robinhood as client
from pyotp import TOTP
from config import *
import numpy as np
from pprint import pprint
import os
from yahoofinance import HistoricalPrices
from time import sleep, time
from tqdm import tqdm
from handles import *
from dates import *


def parse_symbols(d):
    sym = []
    for i in d:
        s = i['symbol']
        if len(s.split('.')) == 1:
            sym.append(s)
    return sym

def get_top_stocks(amt=None):
    top = client.markets.get_top_100()
    return parse_symbols(top)

def get_top_movers(amt=None):
    top = client.markets.get_top_movers()
    return parse_symbols(top)

def get_top_spy(amt=None):
    up = client.markets.get_top_movers_sp500('up')
    down = client.markets.get_top_movers_sp500('down')
    return parse_symbols(up) + parse_symbols(down)

def get_week_symbols():
    stocks = get_top_stocks()
    spy = get_top_spy()
    movers = get_top_movers()
    return list(set(stocks + spy + movers))

def necessary_id(w):
    id_map = {}
    dir_ = f'data/{w}'
    base = sorted(os.listdir(dir_))[0]
    opts = read_json(f'{dir_}/{base}.json')
    for s, o in opts.items():
        id_map[s] = [(i, _o['strike_price'], _o['type']) for i, _o in o.items()]
    return id_map


def get_bars(symbols, t, est=1, cols=['Volume', 'Open', 'Close', 'High', 'Low']):
    bars = {}
    d1, d2 = yfinance_dates()
    for sym in tqdm(symbols, desc=f'Bars for {t}'):
        while True:
            try:
                req = HistoricalPrices(sym, start_date=d1, end_date=d2)
                req_df = req.to_dfs()['Historical Prices']
                
                bars[sym] = [float(req_df[c][0]) for c in cols]
                break
            except Exception as e:
                print(e)
                sleep(est)
    return bars

def collect(path='data', boundary=.1):
    mon, fri = week_range()
    dates = nearest_exps()
    t = today()
    week = f'{mon}_{fri}'
    week_path = f'{path}/{week}'
    day_path = f'{week_path}/{t}'

    if t == mon:
        symbols = get_week_symbols()
        dump_json(f'symbols/weekly/{week}.json', symbols)
    else:
        symbols = read_json(f'symbols/weekly/{week}.json')

    if not os.path.exists(week_path):
        os.mkdir(week_path)
    if not os.path.exists(day_path):
        os.mkdir(day_path)
    if 'bars.json' not in os.listdir(day_path):
        bars = get_bars(symbols, t)
        dump_json(f'{day_path}/bars.json', bars)
    else:
        bars = read_json(f'{day_path}/bars.json')

    for d in dates:
        options = {}
        if t != mon: ids = necessary_id(week)
        if f'{d}.json' not in os.listdir(day_path): 
            for sym in tqdm(symbols, desc=f'Options for {d}: '):
                cp = bars[sym][2]
                try:
                    if t == mon:
                        options[sym] = client.find_options_by_expiration_fast(
                            sym, d, currentPrice=cp, strikeBoundary=boundary
                        )
                    else:
                        options[sym] = client.find_options_by_expiration_fast(
                            sym, d, ids=ids[sym]
                        )
                except:
                    pass
            dump_json(f'{day_path}/{d}.json', options)


if __name__ == '__main__':

    sym = 'AAPL'
    mfa_code = TOTP(qr_code).now()
    login = client.login(username, password, mfa_code=mfa_code)
    #sym = get_week_symbols()
    collect()


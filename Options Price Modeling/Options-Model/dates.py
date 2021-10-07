from datetime import datetime, timedelta

def today():
    return str(datetime.now())[:10]

def yfinance_dates():
    t = datetime.now()
    return str(t - timedelta(days=1))[:10], str(t + timedelta(days=1))[:10]

def time_until_exp(d1, d2, md=252):
    f = '%Y-%m-%d'
    return ((datetime.strptime(d1, f) - datetime.strptime(d2, f)).days - 2)/md
    
def nearest_exps(dn=4, offset=7):
    n = datetime.now()
    wd = n.weekday()
    if wd > 4:
        of = 4 - (wd - 7)
    else:
        of = (4 - wd) + offset
    ofs = [of + i for i in range(0, dn*7, 7)]
    dates = [str(n + timedelta(days=d))[:10] for d in ofs]
    return dates

def week_range():
    t = datetime.now()
    wd = t.weekday()
    if wd < 5:
        mon = t - timedelta(days=wd) 
        fri = t + timedelta(days=4-wd)
    else:
        mon = t + timedelta(days=7-wd)
        fri = t + timedelta(days=11-wd)
    return str(mon)[:10], str(fri)[:10]

if __name__ == '__main__':
    week_range()
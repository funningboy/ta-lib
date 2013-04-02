
import sys
from datetime import datetime

import numpy as np
import talib
import matplotlib.finance as fin
from pylab import show

from pandas import Index, DataFrame, Series
from pandas.core.datetools import BMonthEnd
from pandas import ols


def getQuotes(symbol, start, end):
    """ get stock Quotes from Yahoo """

    quotes = fin.quotes_historical_yahoo(symbol, start, end)
    dates, open, close, high, low, volume = zip(*quotes)

    data = {
        'open': open,
        'close': close,
        'high': high,
        'low': low,
        'volume': volume
    }

    dates = Index([datetime.fromordinal(int(d)) for d in dates])
    return DataFrame(data, index=dates)


def getMA(quotes):
    """ get mv_avg indicator and update org quotes by joining two DataFrame """

    ma5 = talib.MA(quotes['close'],5)
    ma10 = talib.MA(quotes['close'],10)

    data = {
            'ma5' : ma5,
            'ma10': ma10,
            }

    update = DataFrame(data, index=quotes.index)
    return update.join(quotes)


def setEntryRule1(quotes):
    """ set entry rule when ma5 is cross-over ma10 """

    def rule1(quotes, index):
        rst = 1 if quotes['ma5'][index] > quotes['ma10'][index] else 0
        return rst

    quotes['entry'] = [rule1(quotes, index) for index in quotes.index]
    return quotes


def setLeaveRule1(quotes):
    """ set leave rule when the holding day is large than 3 days"""

    def rule1(quotes, position):
        if position - 3 >= 0:
            if quotes['entry'][position-3] == 1:
                return [1, quotes['close'][position] - quotes['close'][position-3]]
        return [0, 0]

    quotes['leave'], quotes['profit'] = zip(*[rule1(quotes, position) for position, index in enumerate(quotes.index)])
    return quotes


def getProfit(quotes):
    """ get profit report """

    print "total profit is : %s" %(sum(quotes['profit']))
    print "-" * 100
    print quotes


def main():
    # get stock info from start to end
    startDate = datetime(2013, 1, 1)
    endDate = datetime(2013, 1, 30)

    # get stock id
    goog = getQuotes('GOOG', startDate, endDate)
    goog = getMA(goog)

    goog = setEntryRule1(goog)
    goog = setLeaveRule1(goog)
    getProfit(goog)

if __name__ == '__main__':
    main()

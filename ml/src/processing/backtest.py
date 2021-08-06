import pandas as pd
import typing

from pandas.tseries.frequencies import to_offset

def backtest_target_strategy(close: 'pd.Series[float]', target: 'pd.Series[float]') -> typing.Tuple[float, float, 'pd.Series[float]']:
    cash_available = 5000
    cash_flow = 0
    lots = 0
    ret_history: pd.Series['float'] = pd.Series(index=target.index)

    for idx, act in target.items():
        price = close[idx]
        
        if act > 0 and cash_available > price:
            to_buy = int(cash_available / (price * (1 + 0.00025)))
            lots += to_buy
            cash_flow += to_buy * price
            cash_available -= to_buy * price * (1 + 0.00025)
        if act < 0 and lots > 0:
            cash_flow += lots * price
            cash_available += lots * price * (1 - 0.00025)
            lots = 0
        
        ret_history[idx] = cash_available + lots * price

    return cash_flow, ret_history

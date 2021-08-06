import plotly.graph_objects as go
import pandas as pd


def make_candlestick(data: pd.DataFrame) -> go.Candlestick:
    return go.Candlestick(x=data.t, high=data.h, low=data.l, open=data.o, close=data.c)

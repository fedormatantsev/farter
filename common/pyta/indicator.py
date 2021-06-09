import typing
import ctypes
import enum
# import pandas as pd
import os
# import plotly.graph_objects as go
# import numpy as np
# import ta.trend

SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))
LIBTA_PATH = os.path.join(SCRIPT_PATH, '..', '..', 'target', 'debug', 'libta_c.dylib')

libta = ctypes.cdll.LoadLibrary(LIBTA_PATH)

libta.create_simple_moving_average.argtypes = [ctypes.c_uint64]
libta.create_simple_moving_average.restype = ctypes.c_void_p

libta.create_exponential_moving_average.argtypes = [ctypes.c_uint64]
libta.create_exponential_moving_average.restype = ctypes.c_void_p

libta.eval_indicator.argtypes = [ctypes.c_void_p, ctypes.c_double, ctypes.POINTER(ctypes.c_double)]
libta.eval_indicator.restype = ctypes.c_int

libta.destroy_indicator.argtypes = [ctypes.c_void_p]


class EvalResult(enum.Enum):
    Ok = 0
    NotReady = 1
    Error = 2


def create_simple_moving_average(args):
    if 'period' not in args:
        raise RuntimeError('SimpleMovingAverage requires period parameter')

    period = args['period']

    if not isinstance(period, int):
        raise RuntimeError(f'SimpleMovingAverage requires period parameter of type int')

    inst = libta.create_simple_moving_average(ctypes.c_uint64(period))

    if not inst:
        raise RuntimeError('Failed to create SimpleMovingAverage instance')

    return inst


def create_exponential_moving_average(args):
    if 'period' not in args:
        raise RuntimeError('ExponentialMovingAverage requires period parameter')

    period = args['period']

    if not isinstance(period, int):
        raise RuntimeError(f'ExponentialMovingAverage requires period parameter of type int')

    inst = libta.create_exponential_moving_average(ctypes.c_uint64(period))

    if not inst:
        raise RuntimeError('Failed to create ExponentialMovingAverage instance')

    return inst


class Indicator:
    def __init__(self, indicator_type: str, **kwargs):
        self._libta = libta

        if indicator_type == 'SimpleMovingAverage':
            self._inst = create_simple_moving_average(kwargs)
        elif indicator_type == 'ExponentialMovingAverage':
            self._inst = create_exponential_moving_average(kwargs)
        else:
            raise RuntimeError(f'Unknown indicator type: {indicator_type}')

    def eval(self, value: float) -> typing.Optional[float]:
        out = ctypes.c_double(0.0)
        res = libta.eval_indicator(self._inst, ctypes.c_double(value), ctypes.byref(out))

        if res == EvalResult.Ok.value:
            return out.value
        elif res == EvalResult.NotReady.value:
            return None
        elif res == EvalResult.Error.value:
            raise RuntimeError('Error during indicator evaluation')
        else:
            RuntimeError(f'Unexpected evaluation return code: {res}')

    def __del__(self):
        self._libta.destroy_indicator(self._inst)


# if __name__ == '__main__':
#     sma = Indicator('SimpleMovingAverage', period=10)
#     ema = Indicator('ExponentialMovingAverage', period=10)
#
#     rand = np.random.randint(0, 100, 50) / 100.0
#     sin = np.sin(np.linspace(0, 6, 50))
#
#     s = pd.Series(sin * 0.8 + rand)
#     sma_data = []
#     ema_data = []
#
#     ref_ema = ta.trend.sma_indicator(s, window=10)
#
#     for elem in s.values:
#         sma_data.append(sma.eval(elem))
#         ema_data.append(ema.eval(elem))
#
#     sma_out = pd.Series(sma_data, dtype=float)
#     ema_out = pd.Series(ema_data, dtype=float)
#
#     fig = go.Figure(data=go.Scatter(x=s.index.values, y=s.values))
#     fig.add_scatter(x=sma_out.index.values, y=sma_out.values)
#     fig.add_scatter(x=ema_out.index.values, y=ema_out.values)
#     fig.add_scatter(x=ref_ema.index.values, y=ref_ema.values)
#     fig.write_html('fig.html', auto_open=True)

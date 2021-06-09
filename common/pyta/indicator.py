import typing
import ctypes
import enum
import os

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

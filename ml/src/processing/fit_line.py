import pandas as pd
import numpy as np


def fit_line(high: pd.Series, low: pd.Series) -> np.array:
    x = high.index.values
    y_high = high.values
    y_low = low.values
    mid_y0 = y_low[0] + (y_high[0] - y_low[0]) / 2.0
    mid_y1 = y_low[-1] + (y_high[-1] - y_low[-1]) / 2.0

    #print(f'mid_y0 {mid_y0}; mid_y1 {mid_y1}')

    a = (mid_y1 - mid_y0) / (x[-1] - x[0])
    b = mid_y0 - a * x[0]

    def _error_fn(a: float, b: float) -> float:
        line = a * x + b
        high_errors = np.square(line - y_high)
        low_errors = np.square(line - y_low)
        return np.sum(high_errors) + np.sum(low_errors)

    def _error_grad(a: float, b: float) -> np.array:
        high_da = 2 * x * (a * x + b - y_high)
        high_db = 2 * (a * x + b - y_high)
        low_da = 2 * x * (a * x + b - y_low)
        low_db = 2 * (a * x + b - y_low)
        return np.array([np.sum(high_da) + np.sum(low_da), np.sum(high_db) + np.sum(low_db)])

    cur_error = _error_fn(a, b)
    gamma = 0.00001

    for step in range(5000):
        grad = _error_grad(a, b)
        a_tmp = a - gamma * grad[0]
        b_tmp = b - gamma * grad[1]
        next_error = _error_fn(a_tmp, b_tmp)
        delta = cur_error - next_error
        #print(f'[{step}] Next point {a_tmp}, {b_tmp}; delta: {delta}; error {next_error}')
        if next_error > cur_error or abs(delta) < 0.001:
            break

        cur_error = next_error
        a = a_tmp
        b = b_tmp
    
    return np.array([a, b])

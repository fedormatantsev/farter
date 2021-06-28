import pandas as pd


def calculate_target(raw_data: pd.DataFrame, threshold: float):
    buffer = []
    close_prices = raw_data.c.values
    gap = 2

    for idx in range(len(close_prices) - gap):
        roc = (close_prices[idx + gap] - close_prices[idx]) / close_prices[idx]

        if roc > threshold:
            buffer.append(1)
        elif roc < -threshold:
            buffer.append(-1)
        else:
            buffer.append(0)

    buffer.extend([None] * gap)

    return pd.Series(data=buffer)

import typing
import pandas as pd


StrategyCallable = typing.Callable[['pd.Series[float]'], float]


def eval_target(close: 'pd.Series[float]',
                window: int,
                target_strategy: StrategyCallable) -> pd.DataFrame:
    indices = []
    actions = []

    for first_idx in range(0, len(close) - window + 1):
        last_idx = first_idx + window
        window_data: 'pd.Series[float]' = close[first_idx:last_idx]
        res = target_strategy(window_data)
        indices.append(first_idx)
        actions.append(res)

    return pd.DataFrame({'actions': actions}, index=indices)

import typing
import pandas as pd
import pyta
import dataclasses

from farter.model import ModelConfig, RelativeStrengthIndexParams


def make_indicator(indicator_params):
    if isinstance(indicator_params, RelativeStrengthIndexParams):
        indicator_type = 'RelativeStrengthIndex'
    else:
        raise RuntimeError(f'Unknown indicator type: {indicator_params}')

    return pyta.Indicator(indicator_type, **dataclasses.asdict(indicator_params))


def calculate_indicators(config: ModelConfig, raw_input: typing.List[pd.DataFrame]) -> typing.List[pd.Series]:
    result = []
    for indicator_config in config.indicators:
        raw_input_idx = config.raw_input.index(indicator_config.source)
        raw_input_data = raw_input[raw_input_idx]

        indicator = make_indicator(indicator_config.indicator_params)

        result.append(indicator.eval(raw_input_data))

    return result

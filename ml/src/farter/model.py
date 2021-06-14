import dataclasses
import datetime
import typing
import yaml
import enum
import os
import hashlib

SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.normpath(os.path.join(SCRIPT_PATH, '..', '..', 'data'))
RAW_DATA_PATH = os.path.join(DATA_PATH, 'raw')
INDICATOR_DATA_PATH = os.path.join(DATA_PATH, 'indicator')
CONFIG_DATA_PATH = os.path.join(DATA_PATH, 'config')


class CandleResolution(enum.Enum):
    ONE_MINUTE = 0
    FIVE_MINUTES = 1
    TEN_MINUTES = 2
    THIRTY_MINUTES = 3
    ONE_HOUR = 4
    ONE_DAY = 4


@dataclasses.dataclass
class RawInputConfig:
    ticker: str
    resolution: CandleResolution
    first_date: datetime.date
    last_date: datetime.date

    def __hash__(self):
        return hash((self.ticker, self.resolution.name, self.first_date.isoformat(), self.last_date.isoformat()))

    def hash(self, sha):
        sha.update(bytes(self.ticker, encoding='UTF8'))
        sha.update(bytes(self.resolution.name, encoding='UTF8'))
        sha.update(bytes(self.first_date.isoformat(), encoding='UTF8'))
        sha.update(bytes(self.last_date.isoformat(), encoding='UTF8'))

    def get_file_path(self) -> str:
        sha = hashlib.sha256()
        self.hash(sha)
        h = sha.hexdigest()

        return os.path.join(RAW_DATA_PATH, f'{str(h)}.csv')


@dataclasses.dataclass
class RelativeStrengthIndexParams:
    period: int

    def __hash__(self):
        # тэг нужен, чтобы различать параметры разных индикаторов
        return hash(('RelativeStrengthIndex', self.period))

    def hash(self, sha):
        sha.update(b'RelativeStrengthIndex')
        sha.update(self.period)


def make_indicator_params(params_dict: typing.Dict):
    indicator_type = params_dict['type'].lower()

    if indicator_type == 'rsi':
        return RelativeStrengthIndexParams(period=params_dict['period'])
    else:
        raise RuntimeError(f'Unknown indicator type {indicator_type}')


@dataclasses.dataclass
class IndicatorConfig:
    source: RawInputConfig
    indicator_params: typing.Union[RelativeStrengthIndexParams]

    def __hash__(self):
        return hash((self.source, self.indicator_params))

    def get_file_path(self) -> str:
        sha = hashlib.sha256()
        self.source.hash(sha)
        self.indicator_params.hash(sha)
        h = sha.hexdigest()

        return os.path.join(INDICATOR_DATA_PATH, f'{str(h)}.csv')


@dataclasses.dataclass
class ModelConfig:
    raw_input: typing.List[RawInputConfig]
    indicators: typing.List[IndicatorConfig]

    @staticmethod
    def load(config_name: str):
        config_path = os.path.join(CONFIG_DATA_PATH, f'{config_name}.yaml')
        with open(config_path, 'r') as config_file:
            config_dict = yaml.load(config_file, Loader=yaml.CFullLoader)
            return ModelConfig.from_dict(config_dict)

    @staticmethod
    def from_dict(config_dict):
        training_data = config_dict['training_data']
        x_definition = config_dict['x_definition']
        y_definition = config_dict['y_definition']

        model_resolution = CandleResolution[training_data['resolution']]
        first_date = datetime.date.fromisoformat(training_data['first_date'])
        last_date = datetime.date.fromisoformat(training_data['last_date'])

        indicators = []
        raw_input = set()
        for x in x_definition:
            ticker = x['ticker']
            raw_input_config = RawInputConfig(ticker=ticker, resolution=model_resolution, first_date=first_date,
                                              last_date=last_date)

            raw_input.add(raw_input_config)
            indicator = IndicatorConfig(source=raw_input_config,
                                        indicator_params=make_indicator_params(x['indicator']))
            indicators.append(indicator)

        raw_input.add(RawInputConfig(ticker=y_definition['ticker'], resolution=model_resolution, first_date=first_date,
                                     last_date=last_date))

        return ModelConfig(raw_input=list(raw_input), indicators=indicators)

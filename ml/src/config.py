import dataclasses
import datetime
import hashlib
import typing
import yaml
import enum
import os


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

    def get_file_name(self) -> str:
        sha = hashlib.sha256()
        sha.update(bytes(self.ticker, encoding='UTF8'))
        sha.update(bytes(self.resolution.name, encoding='UTF8'))
        sha.update(bytes(self.first_date.isoformat(), encoding='UTF8'))
        sha.update(bytes(self.last_date.isoformat(), encoding='UTF8'))
        h = sha.hexdigest()

        return str(h) + '.csv'


@dataclasses.dataclass
class ModelConfig:
    raw_input: typing.List[RawInputConfig]

    @staticmethod
    def from_dict(config_dict):
        training_data = config_dict['training_data']
        x_definition = config_dict['x_definition']
        y_definition = config_dict['y_definition']

        model_resolution = CandleResolution[training_data['resolution']]
        first_date = datetime.date.fromisoformat(training_data['first_date'])
        last_date = datetime.date.fromisoformat(training_data['last_date'])

        tickers = set()
        for x in x_definition:
            tickers.add(x['ticker'])

        tickers.add(y_definition['ticker'])

        raw_input = []
        for ticker in tickers:
            raw_input_config = RawInputConfig(ticker=ticker, resolution=model_resolution, first_date=first_date,
                                              last_date=last_date)
            raw_input.append(raw_input_config)

        return ModelConfig(raw_input=raw_input)


class ConfigLoader:
    def __init__(self):
        script_path = os.path.abspath(os.path.dirname(__file__))
        config_dir = os.path.join(script_path, '..', 'data', 'config')
        self.config_dir = os.path.normpath(config_dir)

    def load_config(self, config_name: str) -> ModelConfig:
        config_path = os.path.join(self.config_dir, f'{config_name}.yaml')

        with open(config_path, 'r') as config_file:
            config_dict = yaml.load(config_file, Loader=yaml.CFullLoader)
            return ModelConfig.from_dict(config_dict)

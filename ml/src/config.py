import dataclasses
import datetime
import hashlib
import typing
import yaml
import enum


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
    def from_file(config_name):
        with open(config_name, 'r') as config_file:
            config_yaml = yaml.load(config_file, Loader=yaml.CFullLoader)

        model_resolution = CandleResolution[config_yaml['training_data']['resolution']]
        first_date = datetime.date.fromisoformat(config_yaml['training_data']['first_date'])
        last_date = datetime.date.fromisoformat(config_yaml['training_data']['last_date'])

        tickers = set()
        for x in config_yaml['x_definition']:
            tickers.add(x['ticker'])

        raw_input = []
        for ticker in tickers:
            raw_input_config = RawInputConfig(ticker=ticker, resolution=model_resolution, first_date=first_date,
                                              last_date=last_date)
            raw_input.append(raw_input_config)

        return ModelConfig(raw_input=raw_input)

import datetime
import dateutil.tz
import pandas as pd
import os

import tinkoff_client

from farter.model import ModelConfig, CandleResolution
from farter.auth_token import get_sandbox_token


def convert_candle_resolution(resolution: CandleResolution):
    return {
        CandleResolution.THIRTY_MINUTES: tinkoff_client.CandleResolution._30MIN
    }[resolution]


class CandleDataFetcher:
    def __init__(self):
        client_configuration = tinkoff_client.Configuration()
        client_configuration.host = 'https://api-invest.tinkoff.ru/openapi/sandbox/'

        self.api_client = tinkoff_client.ApiClient(configuration=client_configuration, header_name='Authorization',
                                                   header_value=f'Bearer {get_sandbox_token()}')
        self.sandbox_api = tinkoff_client.SandboxApi(self.api_client)
        self.market_api = tinkoff_client.MarketApi(self.api_client)

        self.sandbox_api.sandbox_register_post()

    def fetch_raw_data(self, config: ModelConfig):
        res = []

        for input_config in config.raw_input:
            csv_path = input_config.get_file_path()
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                df['t'] = pd.to_datetime(df['t'], utc=True)
                res.append(df)
                continue

            resp = self.market_api.market_search_by_ticker_get(ticker=input_config.ticker)
            if resp.status != 'Ok':
                raise RuntimeError(f'Failed to retrieve instrument data for ticker {input_config.ticker}')

            instr = resp.payload.instruments[0]
            resolution = convert_candle_resolution(input_config.resolution)

            data = self._fetch_raw_data_impl(figi=instr.figi, first_date=input_config.first_date,
                                             last_date=input_config.last_date, resolution=resolution)

            df = pd.DataFrame(data)
            df.to_csv(input_config.get_file_path(), index=False)
            res.append(df)

        return res

    def _fetch_raw_data_impl(self, figi: str, first_date: datetime.date, last_date: datetime.date, resolution: str):
        h = []
        l = []
        o = []
        c = []
        v = []
        t = []

        cur_date = first_date
        while cur_date < last_date:
            _from = datetime.datetime(year=cur_date.year, month=cur_date.month, day=cur_date.day,
                                      tzinfo=dateutil.tz.tzutc())
            to = _from + datetime.timedelta(days=1)

            chunk = self.market_api.market_candles_get(figi=figi, _from=_from, to=to,
                                                       interval=resolution)

            for candle in chunk.payload.candles:
                h.append(candle.h)
                l.append(candle.l)
                o.append(candle.o)
                c.append(candle.c)
                v.append(candle.v)
                t.append(candle.time)

            cur_date += datetime.timedelta(days=1)

        return {
            'h': h,
            'l': l,
            'o': o,
            'c': c,
            'v': v,
            't': t
        }

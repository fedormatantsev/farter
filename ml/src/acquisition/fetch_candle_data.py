from tinkoff_investing_client import AuthenticatedClient
from tinkoff_investing_client.api.sandbox import post_sandbox_register
from tinkoff_investing_client.api.market import get_market_search_by_ticker, get_market_candles
from tinkoff_investing_client.models.candle_resolution import CandleResolution
from tinkoff_investing_client.models.sandbox_register_request import SandboxRegisterRequest

import pandas as pd
import datetime
import dateutil.tz
import typing
import hashlib
import os

from IPython.display import ProgressBar


SANDBOX_URL = 'https://api-invest.tinkoff.ru/openapi/sandbox/'
SANDBOX_AUTH_TOKEN = 't.jrzbG0J7UclBQOqcmHH-oTYzVxjD_BHxmahnEmllcAAWG-oUkMplZsnsrnw7PXCbvs6PnDsHI7L0nj4TO9aFcw'


def register_sandbox_account(client: AuthenticatedClient):
    response = post_sandbox_register.sync_detailed(
        client=client, json_body=SandboxRegisterRequest())
    if response.status_code != 200:
        raise RuntimeError('Failed to register sandbox account')


def get_figi_from_ticker(client: AuthenticatedClient, ticker: str,) -> str:
    response = get_market_search_by_ticker.sync_detailed(
        client=client, ticker=ticker)
    if response.status_code != 200 or not response.parsed.payload.instruments:
        raise RuntimeError(f'Failed to find instrument by ticker {ticker}')

    return response.parsed.payload.instruments[0].figi


def get_cached_file_path(figi: str, first_date: datetime.date, last_date: datetime.date) -> os.PathLike:
    sha = hashlib.sha256()

    for val in [figi, first_date.isoformat(), last_date.isoformat()]:
        sha.update(bytes(val, encoding='UTF-8'))

    file_name = f'{sha.hexdigest()}.yaml'
    script_path = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_path, os.pardir,
                            os.pardir, 'data', 'raw', file_name)

    return csv_path


def get_cached_candle_data(figi: str, first_date: datetime.date, last_date: datetime.date) -> typing.Optional[pd.DataFrame]:
    csv_path = get_cached_file_path(figi, first_date, last_date)

    if not os.path.exists(csv_path):
        return None

    df = pd.read_csv(csv_path)
    df['t'] = pd.to_datetime(df['t'], utc=True)

    return df


def save_candle_date(figi: str, first_date: datetime.date, last_date: datetime.date, df: pd.DataFrame):
    csv_path = get_cached_file_path(figi, first_date, last_date)
    df.to_csv(csv_path, index=False)


def download_candle_data(client: AuthenticatedClient, figi: str, first_date: datetime.date, last_date: datetime.date) -> pd.DataFrame:
    h = []
    l = []
    o = []
    c = []
    v = []
    t = []

    total = last_date.toordinal() - first_date.toordinal()
    progress_bar = ProgressBar(total)
    progress_bar.display()

    current_date = first_date

    while current_date < last_date:
        from_ = datetime.datetime(year=current_date.year, month=current_date.month,
                                  day=current_date.day, tzinfo=dateutil.tz.tzutc())

        delta = datetime.timedelta(days=7)
        current_date = min(current_date + delta, last_date)

        to = datetime.datetime(year=current_date.year, month=current_date.month,
                               day=current_date.day, tzinfo=dateutil.tz.tzutc())

        response = get_market_candles.sync_detailed(
            client=client, figi=figi, from_=from_, to=to, interval=CandleResolution.DAY)

        if response.status_code != 200:
            raise RuntimeError(
                f'Failed to get candles data for time range {from_} {to}: {response.parsed.payload.message}')

        for candle in response.parsed.payload.candles:
            for src, dst in zip([candle.h, candle.l, candle.o, candle.c, candle.v, candle.time], [h, l, o, c, v, t]):
                dst.append(src)

        progress_bar.progress = to.toordinal() - first_date.toordinal()
        progress_bar.update()

    return pd.DataFrame(data={
        'h': h,
        'l': l,
        'o': o,
        'c': c,
        'v': v,
        't': t
    })


def fetch_candle_data(ticker: str, first_date: datetime.date, last_date: datetime.date) -> pd.DataFrame:
    client = AuthenticatedClient(
        base_url=SANDBOX_URL, token=SANDBOX_AUTH_TOKEN)
    register_sandbox_account(client)

    figi = get_figi_from_ticker(client, ticker)

    df = get_cached_candle_data(figi, first_date, last_date)
    if df is not None:
        return df
    
    df = download_candle_data(client, figi, first_date, last_date)
    save_candle_date(figi, first_date, last_date, df)

    return df

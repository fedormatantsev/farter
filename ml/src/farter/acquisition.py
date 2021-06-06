import tinkoff_client

from farter.config import ModelConfig
from farter.auth_token import get_sandbox_token


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
        for input_config in config.raw_input:
            resp = self.market_api.market_search_by_ticker_get(ticker=input_config.ticker)
            if resp.status != 'Ok':
                raise RuntimeError(f'Failed to retrieve instrument data for ticker {input_config.ticker}')

            instr = resp.payload.instruments[0]
            print(instr)

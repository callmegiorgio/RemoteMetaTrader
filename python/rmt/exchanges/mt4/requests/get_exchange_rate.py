from .. import Content
from .  import Request

class GetExchangeRateRequest(Request):
    command = 'getExchangeRate'

    def __init__(self, base_currency: str, quote_currency: str):
        super().__init__()

        self._base_currency = base_currency
        self._quote_currency = quote_currency

    def content(self) -> Content:
        msg = {
            'bcurrency': self._base_currency,
            'qcurrency': self._quote_currency
        }

        return msg
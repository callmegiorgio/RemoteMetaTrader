from .. import Content
from .  import Request

class GetInstrument(Request):
    command = 'getInstrument'

    def __init__(self, symbol: str):
        super().__init__()

        self._symbol = symbol

    def content(self) -> Content:
        msg = {
            'symbol': self._symbol
        }

        return msg
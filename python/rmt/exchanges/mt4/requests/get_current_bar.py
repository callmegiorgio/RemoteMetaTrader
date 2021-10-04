from rmt import Timeframe
from ..  import Content
from .   import Request

class GetCurrentBarRequest(Request):
    command = 'getCurrentBar'

    def __init__(self, symbol: str, timeframe: Timeframe):
        super().__init__()

        if symbol == '':
            raise ValueError('symbol must not be empty')

        self._symbol    = symbol
        self._timeframe = str(timeframe.value)
    
    def content(self) -> Content:
        msg = {
            'symbol': self._symbol,
            'timeframe': self._timeframe
        }
        
        return msg

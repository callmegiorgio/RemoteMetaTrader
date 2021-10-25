from rmt import Timeframe
from ..  import Content
from .   import Request

class GetBar(Request):
    command = 'getBar'

    def __init__(self, symbol: str, index: int, timeframe: Timeframe):
        super().__init__()

        if symbol == '':
            raise ValueError('symbol must not be empty')

        self._symbol    = symbol
        self._index     = index
        self._timeframe = str(timeframe.value)
    
    def content(self) -> Content:
        msg = {
            'symbol': self._symbol,
            'index': self._index,
            'timeframe': self._timeframe
        }
        
        return msg

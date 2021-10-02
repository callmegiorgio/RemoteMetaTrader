from .. import Content
from .  import Request

class WatchSymbolRequest(Request):
    command = 'watchSymbol'

    def __init__(self, symbol: str):
        super().__init__()

        if symbol == '':
            raise ValueError('symbol must not be empty')
        
        self._symbol = symbol
    
    def content(self) -> Content:
        return {
            'symbol': self._symbol
        }
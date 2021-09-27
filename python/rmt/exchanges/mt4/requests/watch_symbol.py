from typing import Dict
from .      import Request

class WatchSymbolRequest(Request):
    command = 'watch_symbol'

    def __init__(self, symbol: str):
        super().__init__()

        if symbol == '':
            raise ValueError('symbol must not be empty')
        
        self._symbol = symbol
    
    def message(self) -> Dict:
        return {
            'symbol': self._symbol
        }
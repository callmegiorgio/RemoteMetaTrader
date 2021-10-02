from datetime import datetime
from typing   import Optional
from ..       import Content
from .        import Request

class GetBarsRequest(Request):
    command = 'getBars'

    def __init__(self,
                 symbol: str,
                 start_time: Optional[datetime],
                 end_time: Optional[datetime]
    ):
        super().__init__()

        if symbol == '':
            raise ValueError('symbol must not be empty')

        self._symbol     = symbol
        self._start_time = start_time
        self._end_time   = end_time
    
    def content(self) -> Content:
        msg = {
            'symbol': self._symbol
        }

        if isinstance(self._start_time, datetime):
            msg['start_time'] = int(self._start_time.timestamp())

        if isinstance(self._end_time, datetime):
            msg['end_time'] = int(self._end_time.timestamp())
        
        return msg

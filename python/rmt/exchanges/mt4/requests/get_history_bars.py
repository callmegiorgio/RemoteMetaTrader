from datetime import datetime
from typing   import Optional
from rmt      import Timeframe
from ..       import Content
from .        import Request

class GetHistoryBars(Request):
    command = 'getHistoryBars'

    def __init__(self,
                 symbol:     str,
                 start_time: Optional[datetime],
                 end_time:   Optional[datetime],
                 timeframe:  Timeframe = Timeframe.M1
    ):
        super().__init__()

        if symbol == '':
            raise ValueError('symbol must not be empty')

        self._symbol     = symbol
        self._start_time = start_time
        self._end_time   = end_time
        self._timeframe  = str(timeframe.value)
    
    def content(self) -> Content:
        msg = {
            'symbol': self._symbol,
            'timeframe': self._timeframe
        }

        if isinstance(self._start_time, datetime):
            msg['start_time'] = int(self._start_time.timestamp())

        if isinstance(self._end_time, datetime):
            msg['end_time'] = int(self._end_time.timestamp())
        
        return msg

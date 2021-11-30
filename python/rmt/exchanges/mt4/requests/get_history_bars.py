from typing   import Optional
from rmt      import Timeframe
from ..       import Content
from .        import Request

class GetHistoryBars(Request):
    command = 'getHistoryBars'

    def __init__(self,
                 symbol:     str,
                 start_time: Optional[str],
                 end_time:   Optional[str],
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

        if self._start_time is not None:
            msg['start_time'] = self._start_time

        if self._end_time is not None:
            msg['end_time'] = self._end_time
        
        return msg

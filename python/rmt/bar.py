from datetime import datetime

class Bar:
    def __init__(self, time: datetime, open: float, high: float, low: float, close: float):
        self._time  = time
        self._open  = float(open)
        self._high  = float(high)
        self._low   = float(low)
        self._close = float(close)
    
    @property
    def time(self) -> datetime:
        return self._time
    
    @property
    def open(self) -> float:
        return self._open
    
    @property
    def high(self) -> float:
        return self._high
    
    @property
    def low(self) -> float:
        return self._low
    
    @property
    def close(self) -> float:
        return self._close
    
    def __str__(self) -> str:
        return \
            """
            Bar(
                time: {}
                open: {}
                high: {}
                low: {}
                close: {}
            )
            """.format(
                self.time,
                self.open,
                self.high,
                self.low,
                self.close
            )
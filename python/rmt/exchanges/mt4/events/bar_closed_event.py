from datetime import datetime, timezone
from .        import Event

class BarClosedEvent(Event):    
    content_layout = {
        'time':   int,
        'open':   float,
        'high':   float,
        'low':    float,
        'close':  float,
        'volume': int
    }

    def symbol(self) -> str:
        return self.dynamic_name

    def time(self) -> datetime:
        return datetime.fromtimestamp(self['time'], timezone.utc)

    def open(self) -> float:
        return self['open']

    def high(self) -> float:
        return self['high']

    def low(self) -> float:
        return self['low']

    def close(self) -> float:
        return self['close']

    def volume(self) -> int:
        return self['volume']
from . import Event

class BarClosedEvent(Event):    
    content_layout = {
        'time':   str,
        'open':   float,
        'high':   float,
        'low':    float,
        'close':  float,
        'volume': int
    }

    def symbol(self) -> str:
        return self.dynamic_name

    def time(self) -> str:
        return self['time']

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
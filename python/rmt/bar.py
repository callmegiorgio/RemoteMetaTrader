from datetime import datetime, timezone
from typing   import Optional, List
from rmt      import Side, SlottedClass

class Bar(SlottedClass):
    __slots__ = [
        '_time',
        '_open',
        '_high',
        '_low',
        '_close',
        '_volume'
    ]

    def __init__(self,
                 time:   datetime,
                 open:   float,
                 high:   float,
                 low:    float,
                 close:  float,
                 volume: int = 0
    ):
        self._time   = time
        self._open   = float(open)
        self._high   = float(high)
        self._low    = float(low)
        self._close  = float(close)
        self._volume = int(volume)
    
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

    @property
    def volume(self) -> int:
        return self._volume

    def side(self) -> Optional[Side]:
        if self.is_bullish():
            return Side.BUY
        elif self.is_bearish():
            return Side.SELL
        else:
            return None

    def is_bullish(self) -> bool:
        return self._close > self._open

    def is_bearish(self) -> bool:
        return self._close < self._open

    def __str__(self) -> str:
        return (
            'Bar(%s, O: %s, H: %s, L: %s, C: %s, V: %s)'
            % (self.time.strftime('%Y-%m-%d %H:%M'), self.open, self.high, self.low, self.close, self.volume)
        )

def read_bars_from_csv(filepath:     str,
                       separator:    str = ',',
                       time_index:   int = 0,
                       open_index:   int = 1, 
                       high_index:   int = 2,
                       low_index:    int = 3,
                       close_index:  int = 4,
                       volume_index: int = 5
) -> List[Bar]:
    bars = []

    with open(filepath, 'r') as file:
        for line in file:
            values = line.split(separator)

            bar = Bar(
                time   = datetime.fromtimestamp(int(values[time_index]), timezone.utc),
                open   = float(values[open_index]),
                high   = float(values[high_index]),
                low    = float(values[low_index]),
                close  = float(values[close_index]),
                volume = int(values[volume_index])
            )

            bars.append(bar)

    return bars
from datetime import datetime
from typing   import Optional
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
                 volume: int
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
        """Returns the side of this bar, if any, or None if bar is neutral."""

        if self.is_bullish():
            return Side.BUY
        elif self.is_bearish():
            return Side.SELL
        else:
            return None

    def is_bullish(self) -> bool:
        """Returns `True` if the close price is greater than the open price, and `False` otherwise."""

        return self._close > self._open

    def is_bearish(self) -> bool:
        """Returns `True` if the close price is less than the open price, and `False` otherwise."""

        return self._close < self._open

    def is_neutral(self) -> bool:
        """Returns `True` if the close price is equal to the open price, and `False` otherwise."""

        return self._close == self._open

    def highest_body_price(self) -> float:
        """Returns the highest of the close and open prices."""

        return max(self.close, self.open)

    def lowest_body_price(self) -> float:
        """Returns the lowest of the close and open prices."""

        return min(self.close, self.open)

    def size(self) -> float:
        """Returns the distance between the high and low prices."""

        return self.high - self.low

    def body_size(self) -> float:
        """Returns the distance between the close and open prices."""

        return abs(self.close - self.open)
    
    def upper_shadow_size(self) -> float:
        """Returns the distance between the highest body price and the high price."""

        return self.high - self.highest_body_price()

    def lower_shadow_size(self) -> float:
        """Returns the distance between the lowest body price and the low price."""

        return self.lowest_body_price() - self.low

    def shadow_size(self) -> float:
        """Returns the sum of the upper shadow and lower shadow sizes."""

        return self.upper_shadow_size() + self.lower_shadow_size()

    def __str__(self) -> str:
        time_str = self.time.strftime('%Y-%m-%d %H:%M+%Z')

        return f'Bar({ time_str }, O: { self.open }, H: { self.high }, L: { self.low }, C: { self.close }, V: { self.volume })'
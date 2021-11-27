from datetime import datetime
from rmt      import SlottedClass

class Tick(SlottedClass):
    """Stores the quotes of an instrument."""

    __slots__ = [ '_time', '_bid', '_ask' ]

    def __init__(self, time: datetime, bid: float, ask: float):
        self._time = time
        self._bid  = float(bid)
        self._ask  = float(ask)

    @property
    def time(self) -> datetime:
        return self._time
    
    @property
    def bid(self) -> float:
        return self._bid

    @property
    def ask(self) -> float:
        return self._ask

    @property
    def spread(self) -> float:
        return abs(self.bid - self.ask)

    def __str__(self) -> str:
        return 'Tick({}, bid: {}, ask: {})'.format(self.time, self.bid, self.ask)
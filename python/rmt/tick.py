from datetime import datetime, timezone
from typing   import Tuple
from rmt      import SlottedClass

class Tick(SlottedClass):
    """Stores the quotes of an instrument."""

    __slots__ = [ '_server_time', '_bid', '_ask' ]

    def __init__(self,
                 server_time: datetime = datetime.fromtimestamp(0, timezone.utc),
                 bid: float = float(0),
                 ask: float = float(0)
    ):
        self._server_time = server_time
        self._bid         = bid
        self._ask         = ask

    @property
    def server_time(self) -> datetime:
        return self._server_time
    
    @property
    def bid(self) -> float:
        return self._bid

    @property
    def ask(self) -> float:
        return self._ask

    def items(self) -> Tuple[datetime, float, float]:
        return (self.server_time, self.bid, self.ask)

    def __str__(self) -> str:
        return 'Tick({}, bid: {}, ask: {})'.format(self.server_time, self.bid, self.ask)
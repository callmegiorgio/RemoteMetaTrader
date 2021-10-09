from datetime import datetime, timezone
from typing   import Tuple, List
from rmt      import SlottedClass

class Tick(SlottedClass):
    """Stores the quotes of an instrument."""

    __slots__ = [ '_server_time', '_bid', '_ask' ]

    def __init__(self,
                 server_time: datetime = datetime.fromtimestamp(0, timezone.utc),
                 bid: float = 0,
                 ask: float = 0
    ):
        self._server_time = server_time
        self._bid         = float(bid)
        self._ask         = float(ask)

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

def read_ticks_from_csv(filepath:   str,
                        separator:  str = ',',
                        time_index: int = 0,
                        bid_index:  int = 1,
                        ask_index:  int = 2
) -> List[Tick]:
    ticks = []

    with open(filepath, 'r') as file:
        for line in file:
            values = line.split(separator)

            tick = Tick(
                server_time = datetime.fromtimestamp(int(values[time_index]), timezone.utc),
                bid         = float(values[bid_index]),
                ask         = float(values[ask_index])
            )

            ticks.append(tick)

    return ticks
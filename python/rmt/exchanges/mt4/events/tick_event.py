from datetime import datetime, timezone
from rmt      import jsonutil, Tick
from ..       import Content
from .        import Event

class TickEvent(Event):
    def __init__(self, symbol: str, content: Content):
        if symbol == '':
            raise ValueError("tick event name is missing instrument symbol")

        if not isinstance(content, list):
            raise ValueError("tick event content is of invalid type (expected: array, got: object)")

        if len(content) != 3:
            raise ValueError('expected 3 elements in tick event array (got: %s)' % len(content))

        timestamp = jsonutil.read_required(content, 0, int)
        bid       = jsonutil.read_required(content, 1, float)
        ask       = jsonutil.read_required(content, 2, float)

        self._symbol = symbol
        self._tick = Tick(
            server_time = datetime.fromtimestamp(timestamp, timezone.utc),
            bid         = bid,
            ask         = ask
        )

    def symbol(self) -> str:
        return self._symbol

    def tick(self) -> Tick:
        return self._tick
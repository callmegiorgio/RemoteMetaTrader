from datetime import datetime
from rmt      import jsonutil, Bar
from ..       import Content
from .        import Event

class BarClosedEvent(Event):
    def __init__(self, symbol: str, content: Content):
        if symbol == '':
            raise ValueError("bar closed event name is missing instrument symbol")

        if not isinstance(content, dict):
            raise ValueError("bar closed event content is of invalid type (expected: object, got: array)")

        self._symbol = symbol
        self._bar = Bar(
            time   = jsonutil.read_required(content, 'time',   datetime),
            open   = jsonutil.read_required(content, 'open',   float),
            high   = jsonutil.read_required(content, 'high',   float),
            low    = jsonutil.read_required(content, 'low',    float),
            close  = jsonutil.read_required(content, 'close',  float),
            volume = jsonutil.read_required(content, 'volume', int)
        )

    def symbol(self) -> str:
        return self._symbol

    def bar(self) -> Bar:
        return self._bar
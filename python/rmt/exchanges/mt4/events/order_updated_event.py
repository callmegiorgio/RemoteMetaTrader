from rmt import jsonutil
from ..  import Content
from .   import Event

class OrderUpdatedEvent(Event):
    def __init__(self, dynamic_name: str, content: Content):
        if not isinstance(content, dict):
            raise ValueError("order event content is of invalid type (expected: object, got: array)")

        self._ticket       = jsonutil.read_required(content, 'ticket',     int)
        self._comment      = jsonutil.read_optional(content, 'comment',    str)
        self._commission   = jsonutil.read_required(content, 'commission', float)
        self._profit       = jsonutil.read_required(content, 'profit',     float)
        self._swap         = jsonutil.read_required(content, 'swap',       float)

    def ticket(self) -> int:
        return self._ticket

    def comment(self) -> str:
        return self._comment

    def commission(self) -> float:
        return self._commission

    def profit(self) -> float:
        return self._profit

    def swap(self) -> float:
        return self._swap

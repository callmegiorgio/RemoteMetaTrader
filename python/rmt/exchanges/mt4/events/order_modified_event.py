from datetime import datetime
from rmt import jsonutil
from ..  import Content
from .   import Event

class OrderModifiedEvent(Event):
    def __init__(self, dynamic_name: str, content: Content):
        if not isinstance(content, dict):
            raise ValueError("order event content is of invalid type (expected: object, got: array)")

        self._ticket      = jsonutil.read_required(content, 'ticket',     int)
        self._open_price  = jsonutil.read_required(content, 'op',         float)
        self._stop_loss   = jsonutil.read_required(content, 'sl',         float)
        self._take_profit = jsonutil.read_required(content, 'tp',         float)
        self._expiration  = jsonutil.read_required(content, 'expiration', datetime)

    def ticket(self) -> int:
        return self._ticket

    def open_price(self) -> float:
        return self._open_price

    def stop_loss(self) -> float:
        return self._stop_loss

    def take_profit(self) -> float:
        return self._take_profit

    def expiration(self) -> datetime:
        return self._expiration

from datetime import datetime
from rmt import jsonutil, OrderStatus
from ..  import Content, OperationCode
from .   import Event

class OrderFinishedEvent(Event):
    def __init__(self, dynamic_name: str, content: Content):
        if not isinstance(content, dict):
            raise ValueError("order event content is of invalid type (expected: object, got: array)")

        opcode = jsonutil.read_required(content, 'opcode', int)
        opcode = OperationCode(opcode)

        self._ticket       = jsonutil.read_required(content, 'ticket',     int)
        self._close_price  = jsonutil.read_required(content, 'cp',         float)
        self._close_time   = jsonutil.read_required(content, 'ct',         datetime)
        self._stop_loss    = jsonutil.read_required(content, 'sl',         float)
        self._take_profit  = jsonutil.read_required(content, 'tp',         float)
        self._expiration   = jsonutil.read_required(content, 'expiration', datetime)
        self._comment      = jsonutil.read_optional(content, 'comment',    str)
        self._commission   = jsonutil.read_required(content, 'commission', float)
        self._profit       = jsonutil.read_required(content, 'profit',     float)
        self._swap         = jsonutil.read_required(content, 'swap',       float)

        if opcode in [OperationCode.BUY, OperationCode.SELL]:
            self._status = OrderStatus.CLOSED
        else:
            if int(self._expiration.timestamp()) > 0 and self._close_time >= self._expiration:
                self._status = OrderStatus.EXPIRED
            else:
                self._status = OrderStatus.CANCELED

    def ticket(self) -> int:
        return self._ticket

    def status(self) -> OrderStatus:
        return self._status

    def close_price(self) -> float:
        return self._close_price

    def close_time(self) -> datetime:
        return self._close_time

    def stop_loss(self) -> float:
        return self._stop_loss

    def take_profit(self) -> float:
        return self._take_profit

    def expiration(self) -> datetime:
        return self._expiration

    def comment(self) -> str:
        return self._comment

    def commission(self) -> float:
        return self._commission

    def profit(self) -> float:
        return self._profit

    def swap(self) -> float:
        return self._swap

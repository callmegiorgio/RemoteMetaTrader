from datetime import datetime, timedelta, timezone
from enum     import IntEnum
from pprint   import pformat

class Side(IntEnum):
    """Trading side or direction."""

    BUY   = 0
    SELL  = 1

class OrderType(IntEnum):
    """Identifies the type of an order."""

    MARKET_ORDER = 0
    LIMIT_ORDER  = 1
    STOP_ORDER   = 2

class OrderStatus(IntEnum):
    """Identifies the status of an order."""

    PENDING          = 0
    CANCELED         = 1
    EXPIRED          = 2
    PARTIALLY_FILLED = 3
    FILLED           = 4
    CLOSED           = 5

class Order:
    """
    Command placed on the exchange server to trade an instrument.

    This class is not intended to be modified or operated directly, but only through
    an instance of the `Exchange` class. All methods of this class are thus read-only,
    since the order's modification only occurs at the server side. Internal values are
    written directly by `Exchange` when a request is made.
    """

    def __init__(self,
                 ticket: int,
                 symbol: str,
                 side: Side,
                 type: OrderType,
                 lots: float,
                 status: OrderStatus,
                 open_price: float,
                 open_time: datetime,
                 close_price: float = 0.0,
                 close_time: datetime = datetime.fromtimestamp(0, timezone.utc),
                 stop_loss: float = 0.0,
                 take_profit: float = 0.0,
                 expiration: datetime = datetime.fromtimestamp(0, timezone.utc),
                 magic_number: int = 0,
                 comment: str = '',
                 commission: float = 0.0,
                 profit: float = 0.0,
                 swap: float = 0.0
    ):
        self._ticket       = ticket
        self._symbol       = symbol
        self._side         = side
        self._type         = type
        self._lots         = lots
        self._status       = status
        self._open_price   = open_price
        self._open_time    = open_time
        self._close_price  = close_price
        self._close_time   = close_time
        self._stop_loss    = stop_loss
        self._take_profit  = take_profit
        self._expiration   = expiration
        self._magic_number = magic_number
        self._comment      = comment
        self._commission   = commission
        self._profit       = profit
        self._swap         = swap

    def ticket(self) -> int:
        return self._ticket

    def symbol(self) -> str:
        return self._symbol

    def side(self) -> Side:
        return self._side

    def type(self) -> OrderType:
        return self._type
    
    def lots(self) -> float:
        return self._lots

    def status(self) -> OrderStatus:
        return self._status

    def open_price(self) -> float:
        return self._open_price

    def open_time(self) -> datetime:
        return self._open_time

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

    def magic_number(self) -> int:
        return self._magic_number

    def comment(self) -> str:
        return self._comment

    def commission(self) -> float:
        return self._commission

    def profit(self) -> float:
        return self._profit

    def swap(self) -> float:
        return self._swap

    def duration(self) -> timedelta:
        if self.close_time() > self.open_time():
            return self.close_time() - self.open_time()
        else:
            return datetime.now(timezone.utc) - self.open_time()

    def __repr__(self) -> str:
        return pformat(vars(self), indent=4, width=1)
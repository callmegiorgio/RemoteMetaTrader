from __future__ import annotations
from datetime   import datetime, timedelta, timezone
from enum       import IntEnum
from typing     import Optional
from rmt        import SlottedClass

class Side(IntEnum):
    """Trade side or direction.
    
    Description
    -----------
    The class `Side` indicates on which side of the market an order is: buy vs sell,
    long vs short, bull vs bear, etc.

    A `Side` object may also be used on side-independent calculations of prices.
    For instance, consider the following code:
    
    ```
    if side == Side.BUY and order.open_price() < 1000:
        print('buy order opened at a price less than 1000')
    elif side == Side.SELL and order.open_price() > 1000:
        print('sell order opened at a price greater than 1000')    
    ```

    The same code can be written as a logic for the buy side, but which works for
    both sides, by using multiplication instead of if-branches:

    ```
    if (order.open_price() * side) < (1000 * side):
        print('order opened at a price [less than, if buy; greater than, if sell] 1000')
    ```

    In the above logic, if `side` is buy, the if-condition behaves the same way as
    `order.open_price() < 1000`. If `side` is sell, however, the logic is evaluated
    as `-order.open_price() < -1000`, which has the same effect of testing for
    `order.open_price() > 1000`. The greater the value of open price is, the smaller
    it is when multiplied by -1, and thus the behavior is the same as the buy case.

    The multiplication style is less verbose and is supposed to be slightly faster,
    since there are less conditions being tested, but may make code a little harder
    to read at first sight. Hence this docstring. It's an idiomatic way of writing
    side-independent code.
    """

    BUY  = 1
    SELL = -1

    def reverse(self) -> Side:
        """Returns the reverse of this side."""

        return Side(self.value * -1)

    def __mul__(self, x: float) -> float:
        return self.value * x

    def __rmul__(self, x: float) -> float:
        return x * self.value

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

class Order(SlottedClass):
    """Stores information about an order."""

    __slots__ = [
        '_symbol',
        '_side',
        '_type',
        '_lots',
        '_status',
        '_open_price',
        '_open_time',
        '_close_price',
        '_close_time',
        '_stop_loss',
        '_take_profit',
        '_expiration',
        '_magic_number',
        '_comment',
        '_commission',
        '_profit',
        '_swap'
    ]

    def __init__(self,
                 symbol:       str,
                 side:         Side,
                 type:         OrderType,
                 lots:         float,
                 status:       OrderStatus,
                 open_price:   float,
                 open_time:    datetime,
                 close_price:  Optional[float]    = None,
                 close_time:   Optional[datetime] = None,
                 stop_loss:    Optional[float]    = None,
                 take_profit:  Optional[float]    = None,
                 expiration:   Optional[datetime] = None,
                 magic_number: int = 0,
                 comment:      str = '',
                 commission:   float = 0.0,
                 profit:       float = 0.0,
                 swap:         float = 0.0
    ):
        self._symbol       = str(symbol)
        self._side         = Side(side)
        self._type         = OrderType(type)
        self._lots         = float(lots)
        self._status       = OrderStatus(status)
        self._open_price   = float(open_price)
        self._open_time    = open_time
        self._close_price  = None if close_price is None else float(close_price)
        self._close_time   = close_time
        self._stop_loss    = None if stop_loss is None else float(stop_loss)
        self._take_profit  = None if take_profit is None else float(take_profit)
        self._expiration   = expiration
        self._magic_number = int(magic_number)
        self._comment      = str(comment)
        self._commission   = float(commission)
        self._profit       = float(profit)
        self._swap         = float(swap)

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

    def close_price(self) -> Optional[float]:
        return self._close_price

    def close_time(self) -> Optional[datetime]:
        return self._close_time

    def stop_loss(self) -> Optional[float]:
        return self._stop_loss

    def take_profit(self) -> Optional[float]:
        return self._take_profit

    def expiration(self) -> Optional[datetime]:
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

    def is_buy(self) -> bool:
        return self._side == Side.BUY

    def is_sell(self) -> bool:
        return self._side == Side.SELL

    def duration(self) -> timedelta:
        last_time = self.close_time()

        if last_time is None:
            last_time = datetime.now(timezone.utc)

        return last_time - self.open_time()            
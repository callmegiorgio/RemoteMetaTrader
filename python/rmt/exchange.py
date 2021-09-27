from datetime     import datetime
from typing       import Dict, List, Optional, Set
from PyQt5.QtCore import QObject, pyqtSignal
from rmt          import Side, Order, Tick, Bar

class Exchange(QObject):
    """Provides access to market data and allows execution of trades."""

    tick_received = pyqtSignal(str, Tick)
    """Event emitted when a quote update of an instrument is received.
    
    This event is emitted by `Exchange.refresh_rates()` when a new tick of
    a subscribed instrument is received. The parameters passed in are the
    instrument's symbol and its new tick.
    
    To access the current tick, irrespective of whether it's a new tick or
    not, `Exchange.get_tick()` may be called.
    """

    order_placed = pyqtSignal(Order)
    """Event emitted when a limit order or a stop order is placed.

    This event is emitted by the methods `Exchange.place_limit_order()` and
    `Exchange.place_stop_order()` when a pending order is placed. The status
    of that pending order is `OrderStatus.PENDING`.

    The parameter passed in is the same order object returned by any of the
    aforementioned methods. You may identify whether the order is a limit order
    or a stop order by calling `Order.type()`.
    """

    order_canceled = pyqtSignal(Order)
    """Event emitted when a limit order or stop order is canceled.

    This event is emitted by `Exchange.cancel_order()` when a pending order
    is canceled. The status of that pending order is `OrderStatus.CANCELED`.

    The parameter passed in is the same order object returned by the aforementioned
    method. You may identify whether the order is a limit order or a stop order
    by calling `Order.type()`.
    """

    order_expired = pyqtSignal(Order)
    """Event emitted when a limit order or stop order expires.
    
    This event is emitted when the exchange automatically cancels a pending order
    once its expiration time is reached. As such, this event is never emitted if
    no expiration time is specified for the order. The status of the expired order
    is `OrderStatus.EXPIRED`.

    The expired order is passed in as a parameter. To identify whether the order is
    a limit order or a stop order, call `Order.type()`.
    """

    order_filled = pyqtSignal(Order)
    """Event emitted when an order is filled.
    
    This event is emitted by `Exchange.place_market_order()` immediately before it
    returns the filled order. In this case, the filled order's status is always
    `OrderStatus.FILLED`.
    
    This event is also called if a pending order, that is, an order returned by a
    call to `Exchange.place_stop_order()` or `Exchange.place_limit_order()`, is filled
    because the market reached its price. In this case, the order may be partially filled,
    in which case the order's status is `OrderStatus.PARTIALLY_FILLED`. Otherwise, the
    order's status is `OrderStatus.FILLED`.

    The filled order is passed in as a parameter. To identify whether the order is a
    marker order, a limit order, or a stop order, call `Order.type()`.
    """

    order_closed = pyqtSignal(Order)
    """Event emitted when a filled order is closed
    
    This event is emitted by `Exchange.close_order()` immediately after it closes an
    order, or if the exchange closed the order for any other reason, such as the market
    reaching the order's Take Profit or Stop Loss prices or a forced sale occuring due to
    failure to meet a margin call. In any case, the order's status is `OrderStatus.CLOSED`.

    Note that only filled orders may be closed. In particular, canceled and expired orders
    never become filled, and thus are never sent by this event.

    The closed order is passed in as a parameter. To identify whether the order is a
    marker order, a limit order, or a stop order, call `Order.type()`.
    """

    def __init__(self):
        super().__init__()

        self._closed_bars: Dict[str, List[Bar]] = {}

    def get_tick(self, symbol: str) -> Tick:
        """Returns the last quotes of an instrument."""

        return Tick()

    def get_bars(self,
                 symbol: str,
                 start_time: Optional[datetime] = None,
                 end_time: Optional[datetime] = None
    ) -> List[Bar]:
        """TODO

        If `start_time` is None, defaults to first bar time.
        If `end_time` is None, defaults to last bar time.
        """

        return []
    
    def get_bar(self, symbol: str, time: datetime) -> Optional[Bar]:
        """Returns a bar of an instrument at a specified time."""

        bars = self.get_bars(symbol, time, time)

        if len(bars) == 0:
            return None
        
        return bars[0]

    def subscribe(self, symbol: str):
        """Begins to receive quote updates of an instrument.

        Parameters
        ----------
        symbol : str
            Instrument symbol.

        Raises
        ------
        NotImplementedError
            If method is not implemented by a subclass.

        UnknownSymbol
            If symbol is not recognized by the exchange.
        """

        raise NotImplementedError(self.subscribe.__name__)

    def subscribe_all(self):
        """Begins to receive quote updates of all instruments.

        Raises
        ------
        NotImplementedError
            If method is not implemented by a subclass.
        
        RequestError
            If request could not be delivered to, or understood by the exchange.
        """

        raise NotImplementedError(self.subscribe_all.__name__)

    def unsubscribe(self, symbol: str):
        """Stops receiving quote updates of an instrument.

        Raises
        ------
        NotImplementedError
            If method is not implemented by a subclass.

        RequestError
            If request could not be delivered to, or understood by the exchange.

        UnknownSymbol
            If symbol is not recognized by the exchange.
        """

        raise NotImplementedError(self.unsubscribe.__name__)

    def unsubscribe_all(self):
        """Stops receiving quote updates of all instruments.

        Raises
        ------
        NotImplementedError
            If method is not implemented by a subclass.

        RequestError
            If request could not be delivered to, or understood by the exchange.
        """

        raise NotImplementedError(self.unsubscribe_all.__name__)

    def subscriptions(self) -> Set[str]:
        """Returns the symbols of all subscribed trading instruments."""

        return set()
    
    def place_market_order(self,
                           symbol: str,
                           side: Side,
                           lots: float,
                           price: float = 0,
                           slippage: int = 0,
                           stop_loss: float = 0,
                           take_profit: float = 0,
                           comment: str = '',
                           magic_number: int = 0
    ) -> Order:
        """Places an order to be executed at market.

        Requests the exchange to execute an order at market price and returns only after the
        order is effectively filled. An exception is raised if an error happens before or
        during the order's execution.

        Warning
        -------
        The returned order is not guaranteed to contain a real value for its open price
        or open time, even if the order was successfully executed. This may happen if the
        exchange, for whatever reason, fails to retrieve the order's data, in which case
        the order's open price and open time are `float(0)` and `datetime.fromdatetime(0, timezone.utc)`,
        respectively. It is up to the user to decide whether to keep the order open or to
        close it. Since `Order.ticket()` is always guaranteed to store a real value, the order
        may be closed by a following call to `self.close_order()`.

        Parameters
        ----------
        symbol : str
            Instrument symbol.

        side : Side
            Order side.

        lots : float
            Order quantity in units of the instrument.

        price : float, optional
            Price at which order is filled. (default: market price)

        slippage : int, optional
            Maximum price slippage. (default: 0)
        
        stop_loss : float, optional
            Stop loss price.
        
        take_profit : float, optional
            Take profit price.

        comment : str, optional
            Order comment text. The last part of the comment may be changed by server.

        magic_number : int, optional
            Order magic number. This may be used as a user-defined identifier.

        Raises
        ------
        NotImplementedError
            If method is not implemented by a subclass.

        ValueError
            If a parameter is provided an invalid value (e.g. `len(symbol) == 0`).

        RequestError
            If request could not be delivered to, or understood by the exchange
            (e.g. network connection dropped, incompatible API version, etc.).

        ExecutionError
            If request was delivered and understood by the exchange, but failed to be
            executed for some reason (e.g. `price` is far off the market range).

        Returns
        -------
        Order
            A filled order.
        """

        raise NotImplementedError(self.place_market_order.__name__)
    
    def place_stop_order(self,
                         symbol: str,
                         side: Side,
                         lots: float,
                         price: float,
                         stop_loss: float = 0,
                         take_profit: float = 0,
                         comment: str = '',
                         magic_number: int = 0,
                         expiration: Optional[datetime] = None
    ) -> Order:
        raise NotImplementedError(self.place_stop_order.__name__)

    def place_limit_order(self,
                          symbol: str,
                          side: Side,
                          lots: float,
                          price: float,
                          stop_loss: float = 0,
                          take_profit: float = 0,
                          comment: str = '',
                          magic_number: int = 0,
                          expiration: Optional[datetime] = None
    ) -> Order:
        raise NotImplementedError(self.place_limit_order.__name__)

    def close_order(self,
                    order: Order,
                    price: float = 0,
                    slippage: int = 0
    ):
        raise NotImplementedError(self.close_order.__name__)

    def partial_close_order(self,
                            order: Order,
                            lots: float,
                            price: float = 0,
                            slippage: int = 0
    ) -> Order:
        raise NotImplementedError(self.partial_close_order.__name__)

    def process_events(self):
        pass
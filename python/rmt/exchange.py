from datetime     import datetime
from typing       import Dict, List, Optional, Set
from PyQt5.QtCore import QObject, pyqtSignal
from rmt          import (Side, Order, Tick, Bar, OrderType, Timeframe,
                          Instrument, Account, error)

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

    @property
    def account(self) -> Account:
        raise error.NotImplementedException(self.__class__, 'account')

    def get_tick(self, symbol: str) -> Tick:
        """Returns the last quotes of an instrument."""

        return error.NotImplementedException(self.__class__, 'get_tick')

    def get_instrument(self, symbol: str) -> Instrument:
        raise error.NotImplementedException(self.__class__, 'get_instrument')

    def get_history_bars(self,
                         symbol:     str,
                         start_time: Optional[datetime] = None,
                         end_time:   Optional[datetime] = None,
                         timeframe:  Timeframe = Timeframe.M1
    ) -> List[Bar]:
        raise error.NotImplementedException(self.__class__, 'get_history_bars')
    
    def get_history_bar(self,
                        symbol:    str,
                        time:      datetime,
                        timeframe: Timeframe = Timeframe.M1
    ) -> Optional[Bar]:
        """Returns a bar of an instrument at a specified time."""

        bars = self.get_history_bars(symbol, time, time, timeframe)

        if len(bars) == 0:
            return None
        
        return bars[0]

    def get_current_bar(self,
                        symbol:    str,
                        timeframe: Timeframe = Timeframe.M1
    ) -> Bar:
        raise error.NotImplementedException(self.__class__, 'get_current_bar')

    def subscribe(self, symbol: str):
        """Begins to receive quote updates of an instrument.

        Parameters
        ----------
        symbol : str
            Instrument symbol.

        Raises
        ------
        UnknownSymbol
            If symbol is not recognized by the exchange.
        """

        raise error.NotImplementedException(self.__class__, 'subscribe')

    def subscribe_all(self):
        """Begins to receive quote updates of all instruments.

        Raises
        ------
        RequestError
            If request could not be delivered to, or understood by the exchange.
        """

        raise error.NotImplementedException(self.__class__, 'subscribe_all')

    def unsubscribe(self, symbol: str):
        """Stops receiving quote updates of an instrument.

        Raises
        ------
        RequestError
            If request could not be delivered to, or understood by the exchange.

        UnknownSymbol
            If symbol is not recognized by the exchange.
        """

        raise error.NotImplementedException(self.__class__, 'unsubscribe')

    def unsubscribe_all(self):
        """Stops receiving quote updates of all instruments.

        Raises
        ------
        RequestError
            If request could not be delivered to, or understood by the exchange.
        """

        raise error.NotImplementedException(self.__class__, 'unsubscribe_all')

    def subscriptions(self) -> Set[str]:
        """Returns the symbols of all subscribed trading instruments."""

        raise error.NotImplementedException(self.__class__, 'subscriptions')

    def place_order(self,
                    symbol:       str,
                    side:         Side,
                    order_type:   OrderType,
                    lots:         float,
                    price:        Optional[float] = None,
                    slippage:     Optional[int]   = None,
                    stop_loss:    Optional[float] = None,
                    take_profit:  Optional[float] = None,
                    comment:      str = '',
                    magic_number: int = 0,
                    expiration:   Optional[datetime] = None
    ) -> int:
        """Places an order to buy or sell an instrument.

        Description
        -----------
        This method requests the exchange server to buy or sell a quantity of an
        instrument at a given price or at market price.

        If `order_type` is `OrderType.MARKET_ORDER`, the exchange is requested to fill
        an order right away, and this method will not return until an order is filled
        or an error occurs. Otherwise, if `order_type` is `OrderType.LIMIT_ORDER` or
        `OrderType.STOP_ORDER`, the exchange is requested to open an order to be filled
        when market price reaches a certain price, and this method will not return
        until an order is opened or an error occurs.
        
        If `price` is specified for a market order, the exchange is requested to fill an
        order at that price. Otherwise, if `price` is `None`, the exchange is requested
        to fill an order at market price.
        
        If `price` is specified for a pending order, the exchange is requested to open a
        pending order which will be filled when market reaches that price. Otherwise,
        if `price` is `None`, the exchange is requested to open an order which will be
        filled when market reaches `mp`, where `mp` is the minimum or maximum allowed
        price (depending on trade `side`) to open a pending order at the time of the last
        known quote of `symbol`.

        `slippage` may be used with a market order to define the maximum price deviation
        from the given price or from the market price. It is broker-defined whether the
        provided slippage will be used or ignored altogether. `slippage` is always ignored
        for pending orders.

        `lots` refer to the quantity of the instrument identified by `symbol` to be bought
        or sold. Note that an order may be filled or opened with a smaller lot size than the
        one provided, in which case that order will be called a *partial order*. It is
        broker-defined whether partial orders may happen. The order filling policy is
        broker-specific and a trader may not change or override it, whether by this method
        call or any other. In other words, if a broker does partial orders, there is nothing
        a trader may do to change that. However, new orders resulting from a partial fill
        will be notified on events.

        ...TODO

        Parameters
        ----------
        symbol : str
            Instrument symbol.

        side : Side
            Order side.

        lots : float
            Quantity of the instrument.

        price : float, optional
            Price at which order is filled. (default: market price for market orders,
            and minimum or maximum order opening price for pending orders)

        slippage : int, optional
            Maximum price slippage. (default: 0)
        
        stop_loss : float, optional
            Stop loss price. (default: no Stop Loss level)
        
        take_profit : float, optional
            Take profit price. (default: no Take Profit level)

        comment : str, optional
            Order comment text. The last part of the comment may be changed by the exchange server.

        magic_number : int, optional
            Order magic number. This may be used as a user-defined identifier.

        Raises
        ------
        ValueError
            If an invalid parameter value is provided.

        RequestError
            If an error occurred before execution of the order.

        ExecutionError
            If an error occurred on the execution of the order.

        Returns
        -------
        int
            Ticket that identifies the placed order.
        """

        raise error.NotImplementedException(self.__class__, 'place_order')

    def modify_order(self,
                     ticket:      int,
                     stop_loss:   Optional[float]    = None,
                     take_profit: Optional[float]    = None,
                     price:       Optional[float]    = None,
                     expiration:  Optional[datetime] = None
    ):
        """Modifies an order.

        Description
        -----------

        Parameters
        ----------
        ticket : int
            Ticket identifying an order.

        stop_loss : float, optional
            New Stop Loss level. (default: current Stop Loss level)
        
        take_profit : float, optional
            New Take Profit level. (default: current Take Profit level)
        
        price : float, optional
            Price at which to fill the order. (default: current open price)
        
        expiration : datetime, optional
            Time at which to expire the order. (default: current expiration time)

        Raises
        ------
        OrderNotFound
            If `ticket` does not identify an order.

        InvalidOrderStatus
            If ...
        """

        raise error.NotImplementedException(self.__class__, 'modify_order')

    def cancel_order(self, ticket: int):
        """Cancels a pending order.
        
        If `ticket` identifies a order whose status is pending, cancels that order and
        returns. Otherwise, if the order is not pending or if cancelation of that order
        fails for some reason, raises an error.

        Parameters
        ----------
        ticket : int
            Ticket that identifies a pending order.
        
        Raises
        ------
        OrderNotFound
            If `ticket` does not identify an order.

        InvalidOrderStatus
            If the order identified by `ticket` is not pending.

        ExecutionError
            If an error occurs while attempting to cancel the order.

        RequestError
            If an error occurs while communicating with the exchange.
        """

        raise error.NotImplementedException(self.__class__, 'cancel_order')

    def close_order(self,
                    ticket:   int,
                    price:    Optional[float] = None,
                    slippage: int             = 0,
                    lots:     Optional[float] = None
    ) -> int:
        """Closes a filled order.

        Description
        -----------
        This method requests the exchange server to close the order identified by
        `ticket`.

        If `ticket` does not identify an order, raises `OrderNotFound`.

        Otherwise, if an order is found and the status of that order is final, namely
        the order is either closed, canceled, or expired, returns `ticket`.

        On the other hand, if the status of that order is pending, raises `InvalidOrderStatus`.

        Otherwise, tries to close the order.
        
        If `price` is a `float` value, the order will be closed at the provided price.
        Otherwise, the value of None will use the current market price. If the order is
        a sell, the current ask price will be used; if the order is a buy, the current
        bid price will be used.

        If a `slippage` is provided, the order will attempt to 

        Parameters
        ----------
        ticket : int
            Ticket that identifies an order.
        
        price : float, optional
            Price at which to close the order. (default: market price)

        slippage : int, optional
            Maximum price slippage. (default: 0)
        
        lots : float, optional
            Lot size of the order to close. (default: whole order)

        Raises
        ------
        OrderNotFound
            If `ticket` does not identify an order.

        

        Requote
            ...
        """

        raise error.NotImplementedException(self.__class__, 'close_order')

    def get_order(self, ticket: int) -> Order:
        """Retrieves information about an order.

        Description
        -----------
        This method requests information from the exchange server about the order
        identified by `ticket`.

        If an order matching `ticket` is found, returns an object of type `Order` which
        stores information about that order. The returned object is guaranteed to hold
        the last known information about that order until a call to `process_events()`,
        `modify_order()`, `close_order()`, or another call to `get_order()` is made,
        since these methods may cause an order to change or may receive updates, and
        may thus make the object returned by this call outdated.
        
        In any case, the reference to the returned object is never updated by this class,
        such that the object effectively represents the state of an order at a given time
        and at no other time.

        Parameters
        ----------
        ticket : int
            Ticket that identifies an order.
        
        Raises
        ------
        OrderNotFound
            If `ticket` does not identify an order.

        ExecutionError
            If any other error occurred at the exchange server while trying to
            retrieve information about the order.

        Returns
        -------
        Order
            object storing information about an order.
        """

        raise error.NotImplementedException(self.__class__, 'place_order')

    def orders(self) -> Dict[int, Order]:
        raise error.NotImplementedException(self.__class__, 'orders')

    def process_events(self):
        raise error.NotImplementedException(self.__class__, 'process_events')
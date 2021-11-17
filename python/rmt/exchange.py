from datetime     import datetime
from typing       import Dict, List, Optional, Set
from PyQt5.QtCore import QObject, pyqtSignal
from rmt          import (Side, Order, Tick, Bar, OrderType, Timeframe,
                          Instrument, Account, error)

class Exchange(QObject):
    """Provides access to market data and allows execution of trades."""

    tick_received = pyqtSignal(str, Tick)
    """Event emitted when a quote update of an instrument is received.
    
    This event is emitted by `process_events()` when a new tick of a subscribed
    instrument is received. The parameters passed in are the instrument's symbol
    and its new tick.
    
    To retrieve the current tick, irrespective of whether it's a new tick or not,
    you may instead call `get_tick()`.
    """

    bar_closed = pyqtSignal(str, Bar)
    """Event emitted when an M1 bar of an instrument is closed.
    
    This event is emitted by `process_events()` when an M1 bar of a subscribed
    instrument is closed. The parameters passed in are the instrument's symbol
    and its closed bar.
    """

    order_opened = pyqtSignal(int)
    """Event emitted when a limit order or a stop order is opened.

    This event is emitted by `process_events()` when an order is opened by the exchange
    server. The order may be have been opened as a result of a call to `place_order()`
    with `OrderType.LIMIT_ORDER` or `OrderType.STOP_ORDER` passed in as a value to the
    parameter `order_type`, or by other means, such as a manual open on the exchange's
    platform.

    The parameter passed in is the open order's ticket, which may be used along with
    `get_order()` to retrieve the associated order object.

    The order notified by this event becomes tracked, meaning that further events on
    that same order are also emitted.
    """

    order_canceled = pyqtSignal(int)
    """Event emitted when a limit order or stop order is canceled.

    This event is emitted by `process_events()` when an order is canceled by the
    exchange server. The order may have been canceled as a result of a call to
    `cancel_order()` or for any other reason, such as a manual cancel on the
    exchange's platform.
    
    The parameter passed in is the ticket of the canceled order. You may identify
    whether that order is a limit order or a stop order by accessing `Order.type` on
    the object returned by `get_order()`.

    Note that this event is only emitted for tracked orders. In particular, if neither
    `order_opened` nor `order_filled` were previously emitted for an order, this event
    is also not emitted for that order.
    """

    order_expired = pyqtSignal(int)
    """Event emitted when a limit order or stop order expires.
    
    This event is emitted by `process_events()` when the exchange automatically
    cancels a pending order due to its expiration time being reached. This may
    only happen to a pending order that has an expiration time.

    The ticket of the expired order is passed in as a parameter.

    Note that this event is only emitted for tracked orders. In particular, if the
    event `order_opened` was not previously emitted for an order, this event is
    also not emitted for that order.
    """

    order_filled = pyqtSignal(int)
    """Event emitted when an order is filled.
    
    This event is emitted by `process_events()` if a pending order becomes filled or
    a new market order is placed. This may happen as a result of `place_order()`
    being previously called, or for another reason, such as a manual fill of a
    market order on the exchange's platform.

    The ticket of the filled order is passed in as a parameter.

    The order notified by this event becomes tracked, meaning that further events on
    that same order are also emitted.
    """

    order_closed = pyqtSignal(int)
    """Event emitted when a filled order is closed.
    
    This event is emitted by `process_events()` if an order is closed by the exchange
    server. This happens as a result of `close_order()` being called or another
    reason, such as a manual close of an order on the exchange's platform, the market
    reaching a previously set Take Profit or Stop Loss level, or a forced sale occuring
    due to an account's failure to meet a margin call.

    The ticket of the closed order is passed in as a parameter.

    Note that this event is only emitted for tracked orders. In particular, if neither
    `order_opened` nor `order_filled` were previously emitted for an order, this event
    is also not emitted for that order.
    """

    order_modified = pyqtSignal(int)
    """Event emitted when an order is modified.
    
    This event is emitted by `process_events()` if a user-modifiable property of an
    order, namely a pending order's open price and expiration time, and an active
    order's Stop Loss and Take Profit level, is changed. This happens if
    `modify_order()` is called or a similar operation is manually performed on
    the exchange's platform.

    The parameter passed in is the ticket of the modified order.

    Note that this event is only emitted for tracked orders. In particular, if neither
    `order_opened` nor `order_filled` were previously emitted for an order, this event
    is also not emitted for that order.
    """

    order_updated = pyqtSignal(int)
    """Event emitted when a dynamic property of an order is changed.
    
    This event is emitted by `process_events()` if any of the dynamic properties of
    an order, namely an order's comment, commission, profit, and swap, is changed.
    Since these are properties which a trader has no control over, no method call
    of this class will cause this event to be emitted, only changes in the market
    itself will do it.

    The ticket of the updated order is passed in as a parameter.

    Note that this event is only emitted for tracked orders. In particular, if neither
    `order_opened` nor `order_filled` were previously emitted for an order, this event
    is also not emitted for that order.
    """

    account_updated = pyqtSignal(Account)
    """Event emitted when a property of the connected account is changed.
    
    This event is emitted by `process_events()` if a property of the `Exchange.account`
    object is changed. In particular, this happens when an equity-related property
    such as `Account.equity` and `Account.balance` is changed.

    The parameter passed in is the object `self.account`.
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
        """Retrieves information about an instrument.

        Parameters
        ----------
        symbol : str
            Instrument symbol.

        Raises
        ------
        InvalidSymbol
            If symbol does not identify an instrument on the exchange.
        
        Returns
        -------
        Instrument
            object storing information about the instrument.
        """

        raise error.NotImplementedException(self.__class__, 'get_instrument')

    def get_instruments(self) -> List[Instrument]:
        """Retrieves all instruments on this exchange."""

        raise error.NotImplementedException(self.__class__, 'get_instruments')

    def get_bar(self,
                symbol: str,
                index: int = 0,
                timeframe: Timeframe = Timeframe.M1
    ) -> Bar:
        """Retrieves a bar of symbol at index.
        
        The method `get_bar()` retrieves a bar in a symbol's list of bars ordered
        descendingly by open time. That is, from the most recent bar to the least
        recent one.
        """

        raise error.NotImplementedException(self.__class__, 'get_bar')

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

    def subscribe(self, symbol: str) -> None:
        """Begins to receive quote updates of an instrument.

        Parameters
        ----------
        symbol : str
            Instrument symbol.

        Raises
        ------
        InvalidSymbol
            If symbol does not identify an instrument on the exchange.
        """

        raise error.NotImplementedException(self.__class__, 'subscribe')

    def subscribe_all(self) -> None:
        """Begins to receive quote updates of all instruments.

        Raises
        ------
        RequestError
            If request could not be delivered to, or understood by the exchange.
        """

        raise error.NotImplementedException(self.__class__, 'subscribe_all')

    def unsubscribe(self, symbol: str) -> None:
        """Stops receiving quote updates of an instrument.

        Raises
        ------
        RequestError
            If request could not be delivered to, or understood by the exchange.

        InvalidSymbol
            If symbol does not identify an instrument on the exchange.
        """

        raise error.NotImplementedException(self.__class__, 'unsubscribe')

    def unsubscribe_all(self) -> None:
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
        """Places an order to buy or sell a contract of an instrument.

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
            If a parameter has an invalid value.

        OffQuotes
            If price is off a limit set by the exchange.

        Requote
            If order is a market order and the given price is outdated.

        RequestError
            If an error occurred before execution of the order.

        ExecutionError
            If an error occurred on the execution of the order.

        Returns
        -------
        int
            Ticket that identifies the order placed.
        """

        raise error.NotImplementedException(self.__class__, 'place_order')

    def modify_order(self,
                     ticket:      int,
                     stop_loss:   Optional[float]    = None,
                     take_profit: Optional[float]    = None,
                     price:       Optional[float]    = None,
                     expiration:  Optional[datetime] = None
    ) -> None:
        """Modifies a pending or filled order.

        Description
        -----------
        This method allows changing the Take Profit and Stop Loss levels of a pending
        or filled order identified by `ticket`.

        If that order is pending, this method also allows modification of its open price
        and expiration time, both of which are ignored if that order's status is filled.
        
        If `ticket` does not identify an order, or if the order is neither pending nor
        filled, or if modification fails for some reason, raises an error. Otherwise,
        this method returns successfully if either an order has been modified or the
        order's properties are left unchanged.

        If all parameters are None, calling this method has no effect.

        Parameters
        ----------
        ticket : int
            Ticket that identifies a filled or pending order.

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
        RequestError
            If an error occurs while communicating with the exchange.

        RequestTimeout
            If exchange takes too long to reply to the request.

        InvalidTicket
            If `ticket` does not identify an order.

        InvalidOrderStatus
            If order is not pending or filled.

        ExecutionError
            If an error occurs while attempting to modify the order.
        """

        raise error.NotImplementedException(self.__class__, 'modify_order')

    def cancel_order(self, ticket: int) -> None:
        """Cancels a pending order.

        Description
        -----------
        
        If `ticket` identifies an order whose status is pending, cancels that order and
        returns. Otherwise, if the order is not pending or if cancelation of that order
        fails for some reason, raises an error.

        Parameters
        ----------
        ticket : int
            Ticket that identifies a pending order.
        
        Raises
        ------
        InvalidTicket
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

        If `ticket` does not identify an order, raises `InvalidTicket`.

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
        InvalidTicket
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
        InvalidTicket
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

    def get_exchange_rate(self, base_currency: str, quote_currency: str) -> float:
        """Retrieves the exchange rate of two currencies.

        Parameters
        ----------
        base_currency : str
            A base currency.
        
        quote_currency : str
            A quote currency.

        Raises
        ------
        ExchangeRateError
            If no rate is found for the currency pair.

        Returns
        -------
        float
            Exchange rate of the currencies.
        """

        return error.NotImplementedException(self.__class__, 'get_exchange_rate')

    def orders(self) -> Dict[int, Order]:
        raise error.NotImplementedException(self.__class__, 'orders')

    def process_events(self) -> None:
        raise error.NotImplementedException(self.__class__, 'process_events')
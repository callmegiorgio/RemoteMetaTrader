import rmt, pytz, logging
from datetime     import datetime, timedelta, tzinfo
from typing       import Optional, Set
from pprint       import pformat
from functools    import singledispatchmethod
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from rmt          import (
    Exchange, Tick, Bar, Performance, Instrument, Account,
    Timeframe, Order, Side, OrderType, OrderStatus, SlottedClass
)

class TimezonedTick(Tick):
    __slots__ = ['_strategy']

    def __init__(self, strategy, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._strategy = strategy

    @property
    def time(self) -> datetime:
        return super().time.astimezone(self._strategy.timezone)

class TimezonedBar(Bar):
    __slots__ = ['_strategy']

    def __init__(self, strategy, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._strategy = strategy

    @property
    def time(self) -> datetime:
        return super().time.astimezone(self._strategy.timezone)

class TimezonedOrder(SlottedClass):
    """Wraps a reference to an order along with a strategy for accessing the
    strategy's timezone. This allows orders returned by `Strategy.get_order()` to refer to the underlying order object,
    even if:
    1. A member of the underlying order object (such as `Order.status`) is changed;
    2. `Strategy.timezone` is changed.

    >>> strategy = Strategy(...)
    >>> strategy.timezone
    'UTC'
    >>> order = strategy.get_order(ticket)
    >>> repr(order.open_time)
    datetime.datetime(2020, 11, 23, 14, 31, tzinfo=<UTC>)
    >>> strategy.timezone = pytz.timezone('America/New_York')
    >>> repr(order.open_time)
    datetime.datetime(2020, 11, 23, 9, 31, tzinfo=<DstTzInfo 'America/New_York' EST-1 day, 19:00:00 STD>)
    """

    __slots__ = ['_order', '_strategy']

    def __init__(self, order: Order, strategy):
        super().__init__()

        self._order    = order
        self._strategy = strategy
    
    @property
    def timezone(self) -> tzinfo:
        return self._strategy.timezone

    @property
    def ticket(self) -> int:
        return self._order._ticket

    @property
    def symbol(self) -> str:
        return self._order._symbol

    @property
    def side(self) -> Side:
        return self._order._side

    @property
    def type(self) -> OrderType:
        return self._order._type
    
    @property
    def lots(self) -> float:
        return self._order._lots

    @property
    def status(self) -> OrderStatus:
        return self._order._status

    @property
    def open_price(self) -> float:
        return self._order._open_price

    @property
    def open_time(self) -> datetime:
        return self._order.open_time.astimezone(self.timezone)

    @property
    def close_price(self) -> Optional[float]:
        return self._order._close_price

    @property
    def close_time(self) -> Optional[datetime]:
        if self._order.close_time is None:
            return None
        else:
            return self._order.close_time.astimezone(self.timezone)

    @property
    def stop_loss(self) -> Optional[float]:
        return self._order._stop_loss

    @property
    def take_profit(self) -> Optional[float]:
        return self._order._take_profit

    @property
    def expiration(self) -> Optional[datetime]:
        if self._order.expiration is None:
            return None
        else:
            return self._order.expiration.astimezone(self.timezone)

    @property
    def magic_number(self) -> int:
        return self._order._magic_number

    @property
    def comment(self) -> str:
        return self._order._comment

    @property
    def commission(self) -> float:
        return self._order._commission

    @property
    def profit(self) -> float:
        return self._order._profit

    @property
    def swap(self) -> float:
        return self._order.swap

    def is_buy(self) -> bool:
        return self._order.is_buy()

    def is_sell(self) -> bool:
        return self._order.is_sell()

    def duration(self) -> timedelta:
        return self._order.duration()

    def __repr__(self) -> str:
        obj = {}

        for attr in self._order.__slots__:
            value = getattr(self._order, attr)

            if isinstance(value, datetime):
                value = value.astimezone(self.timezone)

            obj[attr] = value

        return pformat(obj, indent=4, width=1)

class Strategy(QObject):
    """
    Building block of algorithmic trading.

    Description
    -----------
    The class `Strategy` draws a line separating manual trading from automated trading.
    While manual trades may be done by invoking methods of an `Exchange` directly,
    this class is intended to be used for a machine-driven form of trading.

    It's part of the design of this class to compartimentalize trade execution by
    tracking `Strategy`-made orders and keeping trade operations isolated from the
    `Exchange` which a strategy depends on. For that reason, the `Exchange` which
    a strategy is running on is purposefully not made available, whether as a method
    or an attribute. This is because orders placed by `Strategy` or its subclasses
    are expected to be made by `Strategy.place_order()`, not `Exchange.place_order()`.
    The same applies to all other `Exchange`-based methods, such as `Strategy.close_order()`,
    `Strategy.get_order()`, etc.

    Instances of `Strategy` are expected to work mainly with a main trading instrument.
    This is also part of the design of this class, since arbitrage is not inherent to
    all strategies. While some strategies may be developed for one instrument only,
    other strategies may be developed for many instruments. In the latter case, a
    same strategy may be run with different instruments by creating several instances
    of it:

    ```
    eurusd_strategy = Strategy(exchange, 'EURUSD')
    usdjpy_strategy = Strategy(exchange, 'USDJPY')
    ```

    If arbitrage or a similar logic is required by a strategy, methods for retrieving
    data of another symbol are provided, but the strategy must have a main instrument
    nonetheless:
    
    >>> arbitrage_strategy = Strategy(exchange, 'EURUSD')
    >>> arbitrage_strategy.instrument.symbol
    'EURUSD'
    >>> arbitrage_strategy.get_bar()
    <current EURUSD M1 bar>
    >>> arbitrage_strategy.get_bar(symbol='USDJPY')
    <current USDJPY M1 bar>
    """

    tick_received  = pyqtSignal(Tick)
    bar_closed     = pyqtSignal(Bar)
    order_opened   = pyqtSignal(int)
    order_expired  = pyqtSignal(int)
    order_canceled = pyqtSignal(int)
    order_modified = pyqtSignal(int)
    order_filled   = pyqtSignal(int)
    order_closed   = pyqtSignal(int)

    def __init__(self, exchange: Exchange, symbol: str):
        super().__init__()

        exchange.subscribe(symbol)

        self._exchange   = exchange
        self._instrument = exchange.get_instrument(symbol)

        self._timezone  = pytz.utc
        self._last_tick = self._exchange.get_tick(self.instrument.symbol)

        self._active_orders: Set[int] = set()
        self._history_orders: Set[int] = set()

        self._exchange.tick_received.connect(self._notify_tick_received)
        self._exchange.bar_closed.connect(self._notify_bar_closed)
        self._exchange.order_opened.connect(self._notify_order_opened)
        self._exchange.order_expired.connect(self._notify_order_expired)
        self._exchange.order_canceled.connect(self._notify_order_canceled)
        self._exchange.order_modified.connect(self._notify_order_modified)
        self._exchange.order_filled.connect(self._notify_order_filled)
        self._exchange.order_closed.connect(self._notify_order_closed)

        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.info(
            "started strategy with main instrument '%s' on server '%s'",
            self.instrument.symbol,
            self.account.server
        )

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    @property
    def account(self) -> Account:
        return self._exchange.account

    @property
    def instrument(self) -> Instrument:
        """Main instrument traded by this strategy."""

        return self._instrument

    @property
    def tick(self) -> Tick:
        """Returns the last received tick on the strategy's instrument."""

        return self._last_tick

    @property
    def timezone(self) -> tzinfo:
        """Returns the timezone used by the strategy."""

        return self._timezone

    @timezone.setter
    def timezone(self, timezone: tzinfo):
        """Sets the timezone to be used by the strategy.
        
        This will cause all datetime-related values coming from this strategy
        or its associated objects to be in the given `timezone`. In particular,
        `Order`, `Tick`, and `Bar` objects will have their datetime members in the
        given timezone.
        """

        self._timezone  = timezone
        self._last_tick = self.astimezone(self._last_tick)

    @singledispatchmethod
    def astimezone(self, o: object):
        raise rmt.error.NotImplementedException(self.__class__, 'astimezone')

    @astimezone.register
    def _(self, tick: Tick) -> Tick:
        if tick.time.tzinfo == self._timezone:
            return tick
        else:
            return TimezonedTick(
                strategy = self,
                time     = tick.time,
                bid      = tick.bid,
                ask      = tick.ask
            )

    @astimezone.register
    def _(self, bar: Bar) -> Bar:
        if bar.time.tzinfo == self._timezone:
            return bar
        else:
            return TimezonedBar(
                strategy = self,
                time     = bar.time,
                open     = bar.open,
                high     = bar.high,
                low      = bar.low,
                close    = bar.close,
                volume   = bar.volume
            )

    @astimezone.register
    def _(self, order: Order) -> Order:
        return TimezonedOrder(order, self)

    def active_orders(self) -> Set[int]:
        """Set of active orders placed by this strategy."""
        
        return self._active_orders.copy()

    def history_orders(self) -> Set[int]:
        """Set of history orders which were placed by this strategy."""

        return self._history_orders.copy()

    def performance(self) -> Performance:
        """Performance of this strategy, calculated by its closed orders."""

        orders = [self._exchange.get_order(ticket) for ticket in self._history_orders]

        return Performance(orders, 2)

    def get_tick(self, symbol: str) -> Tick:
        """Retrieves the last received tick on an instrument."""

        return self._exchange.get_tick(symbol)

    def get_instrument(self, symbol: str) -> Instrument:
        """Retrieves an instrument from the exchange which this strategy is running on."""

        return self._exchange.get_instrument(symbol)

    def get_bar(self, index: int = 0, timeframe: Timeframe = Timeframe.M1, symbol: str = ...) -> Bar:
        """Retrieves a bar of an instrument.
        
        If `symbol` is provided, retrieves a bar of the instrument identified by `symbol`.
        Otherwise, retrieves a bar of this strategy's main instrument.
        """

        if symbol is Ellipsis:
            symbol = self.instrument.symbol

        bar = self._exchange.get_bar(symbol=symbol, index=index, timeframe=timeframe)

        return self.astimezone(bar)

    def get_history_bar(self,
                        time:      datetime,
                        timeframe: Timeframe = Timeframe.M1,
                        symbol:    str = ...
    ) -> Optional[Bar]:
        if symbol is Ellipsis:
            symbol = self.instrument.symbol

        bar = self._exchange.get_history_bar(symbol=symbol, time=time, timeframe=timeframe)

        return self.astimezone(bar)

    def get_order(self, ticket: int) -> Order:
        """Retrieves information of an order placed by this strategy.
        
        Parameters
        ----------
        ticket : int
            Ticket that identifies an order placed by this strategy.

        Raises
        ------
        InvalidTicket
            If `ticket` does not identify an order placed by this strategy.
        """

        if ticket in self._active_orders or ticket in self._history_orders:
            order = self._exchange.get_order(ticket)

            return self.astimezone(order)

        raise rmt.error.InvalidTicket(ticket)

    def get_exchange_rate(self, base_currency: str, quote_currency: str) -> float:
        return self._exchange.get_exchange_rate(base_currency=base_currency, quote_currency=quote_currency)

    def place_order(self,
                    side:         Side,
                    order_type:   OrderType,
                    lots:         float,
                    price:        Optional[float] = None,
                    slippage:     Optional[int]   = None,
                    stop_loss:    Optional[float] = None,
                    take_profit:  Optional[float] = None,
                    comment:      str = '',
                    magic_number: int = 0,
                    expiration:   Optional[datetime] = None,
                    symbol:       Optional[str]      = None
    ) -> int:
        if symbol is None:
            symbol = self.instrument.symbol

        ticket = self._exchange.place_order(
            side         = side,
            order_type   = order_type,
            lots         = lots,
            price        = price,
            slippage     = slippage,
            stop_loss    = stop_loss,
            take_profit  = take_profit,
            symbol       = symbol,
            comment      = comment,
            magic_number = magic_number,
            expiration   = expiration
        )

        self._active_orders.add(ticket)

        return ticket

    def modify_order(self,
                     ticket: int,
                     stop_loss:   Optional[float]    = None,
                     take_profit: Optional[float]    = None,
                     price:       Optional[float]    = None,
                     expiration:  Optional[datetime] = None
    ) -> None:
        if ticket not in self._active_orders:
            raise rmt.error.InvalidTicket(ticket)
        
        self._exchange.modify_order(
            ticket      = ticket,
            stop_loss   = stop_loss,
            take_profit = take_profit,
            price       = price,
            expiration  = expiration
        )

    def cancel_order(self, ticket: int) -> None:
        if ticket not in self._active_orders:
            raise rmt.error.InvalidTicket(ticket)

        self._exchange.cancel_order(ticket)

    def close_order(self,
                    ticket:   int,
                    price:    Optional[float] = None,
                    slippage: int             = 0,
                    lots:     Optional[float] = None
    ) -> int:
        if ticket not in self._active_orders:
            raise rmt.error.InvalidTicket(ticket)

        new_ticket = self._exchange.close_order(
            ticket   = ticket,
            price    = price,
            slippage = slippage,
            lots     = lots
        )

        return new_ticket

    #===============================================================================
    # Internals
    #===============================================================================
    @pyqtSlot(str, Tick)
    def _notify_tick_received(self, symbol: str, tick: Tick):
        if symbol != self.instrument.symbol:
            return

        self._last_tick = self.astimezone(tick)
        self.tick_received.emit(self._last_tick)

    @pyqtSlot(str, Bar)
    def _notify_bar_closed(self, symbol: str, bar: Bar):
        if symbol != self.instrument.symbol:
            return

        self.bar_closed.emit(self.astimezone(bar))

    @pyqtSlot(int)
    def _notify_order_opened(self, ticket: int):
        if ticket in self._active_orders:
            self.order_opened.emit(ticket)

    @pyqtSlot(int)
    def _notify_order_canceled(self, ticket: int):
        if ticket in self._active_orders:
            self._active_orders.remove(ticket)
            self._history_orders.add(ticket)

            self.order_canceled.emit(ticket)

    @pyqtSlot(int)
    def _notify_order_expired(self, ticket: int):
        if ticket in self._active_orders:
            self._active_orders.remove(ticket)
            self._history_orders.add(ticket)

            self.order_expired.emit(ticket)

    @pyqtSlot(int)
    def _notify_order_modified(self, ticket: int):
        if ticket in self._active_orders:
            self.order_modified.emit(ticket)

    @pyqtSlot(int)
    def _notify_order_filled(self, ticket: int):
        if ticket in self._active_orders:
            self.order_filled.emit(ticket)

    @pyqtSlot(int)
    def _notify_order_closed(self, ticket: int):
        if ticket in self._active_orders:
            self._active_orders.remove(ticket)
            self._history_orders.add(ticket)

            self.order_closed.emit(ticket)
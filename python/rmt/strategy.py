import rmt
from datetime     import datetime
from typing       import Optional, Set
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from rmt          import (
    Exchange, Tick, Bar, Performance, Instrument,
    Timeframe, Order, Side, OrderType
)

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

        self._last_closed_bar_time: Optional[datetime] = None

        self._last_tick: Optional[Tick] = None
        
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

    @property
    def instrument(self) -> Instrument:
        """Main instrument traded by this strategy."""

        return self._instrument

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

    def get_tick(self) -> Tick:
        """Retrieves the last received tick on the strategy's instrument."""

        if self._last_tick is None:
            self._last_tick = self._exchange.get_tick(self.instrument.symbol)

        return self._last_tick

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

        return self._exchange.get_bar(symbol=symbol, index=index, timeframe=timeframe)

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
            return self._exchange.get_order(ticket)

        raise rmt.error.InvalidTicket(ticket)

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

        self._active_orders.remove(ticket)
        self._history_orders.add(ticket)

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

        self._active_orders.remove(ticket)

        if new_ticket != ticket:
            self._active_orders.add(new_ticket)

        self._history_orders.add(ticket)

        return new_ticket

    #===============================================================================
    # Internals
    #===============================================================================
    @pyqtSlot(str, Tick)
    def _notify_tick_received(self, symbol: str, tick: Tick):
        if symbol != self.instrument.symbol:
            return

        self._last_tick = tick

        self.tick_received.emit(tick)

    @pyqtSlot(str, Bar)
    def _notify_bar_closed(self, symbol: str, bar: Bar):
        if symbol != self.instrument.symbol:
            return

        self.bar_closed.emit(bar)

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
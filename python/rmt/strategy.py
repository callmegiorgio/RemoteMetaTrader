from datetime     import datetime, timedelta
from typing       import Optional
from PyQt5.QtCore import QObject, pyqtSlot
from rmt          import Exchange, Tick, Bar

class Strategy(QObject):
    """
    Building block of algorithmic trading.

    The strategy class draws a line separating manual trading from automated trading.
    While manual trades may be done by invoking methods of an `Exchange` directly,
    the strategy class allows a machine-driven form of trading.

    The methods `Strategy.on_tick()` and `Strategy.on_bar_closed()` are provided for
    strategy-specific logic, and should be overloaded by subclasses.

    After a bar closes, `Strategy.on_bar_closed()` is invoked immediately before
    `Strategy.on_tick()`.
    """

    def __init__(self, exchange: Exchange):
        super().__init__()

        self._exchange = exchange
        self._exchange.tick_received.connect(self._on_tick_received)
        self._last_closed_bar_time: Optional[datetime] = None

    @property
    def exchange(self) -> Exchange:
        """The exchange on which the strategy is running."""

        return self._exchange

    def on_tick(self, symbol: str, server_time: datetime, bid: float, ask: float):
        """Method invoked when an instrument's new quotes is received."""

        pass

    def on_bar_closed(self, symbol: str, bar: Bar):
        """Method invoked when an instrument's bar is closed."""

        pass

    #===============================================================================
    # Internals
    #===============================================================================
    @pyqtSlot(str, Tick)
    def _on_tick_received(self, symbol: str, tick: Tick):
        last_closed_bar_time = tick.server_time.replace(second=0) - timedelta(0, 60, 0)

        if self._last_closed_bar_time is None:
            self._last_closed_bar_time = last_closed_bar_time
        elif self._last_closed_bar_time != last_closed_bar_time:
            self._last_closed_bar_time = last_closed_bar_time

            closed_bar = self.exchange.get_bar(symbol, last_closed_bar_time)

            if closed_bar is not None:
                self.on_bar_closed(symbol, closed_bar)

        self.on_tick(symbol, tick.server_time, tick.bid, tick.ask)
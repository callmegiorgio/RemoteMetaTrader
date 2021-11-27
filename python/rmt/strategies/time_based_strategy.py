from typing       import Callable, List, Tuple
from PyQt5.QtCore import pyqtSlot
from rmt          import Strategy, Exchange, Tick, TimePredicate

TickHandler = Callable[[Tick], None]
"""A tick handler is a callable object that takes a `Tick` parameter."""

class TimeBasedStrategy(Strategy):
    """Implements a strategy that executes tick handlers at specific tick times.

    Description
    -----------
    This class extends `Strategy` to provide an abstraction for trading strategies
    which are not interested in each and every received tick, but that instead have
    their logic defined on specific time periods.

    For that, this class stores objects of type `TickHandler` along with objects
    of type `TimePredicate`, and hooks `Strategy.tick_received` to implement the
    behavior of calling a tick handler when its associated time predicate is `True`.

    One use case for a time-based strategy is an index instrument which has high
    volatility at its opening time. Taking NASDAQ 100 as an example instrument of
    symbol "US100" that opens at 02:30 PM (GMT), we have:
    
    ```
    nasdaq_strategy = TimeBasedStrategy(exchange, 'US100')
    nasdaq_strategy.add_tick_handler(predicate.AtMinute(hour=14, minute=30), on_nasdaq_opening_tick)
    ```

    This strategy will invoke the function `on_nasdaq_opening_tick()` for every tick
    received at a 02:30 PM bar.
    """

    def __init__(self, exchange: Exchange, symbol: str):
        super().__init__(exchange, symbol)

        self._tick_handlers: List[Tuple[TimePredicate, TickHandler]] = []

        self.tick_received.connect(self._notify_tick_handlers)

    def add_tick_handler(self, pred: TimePredicate, handler: TickHandler):
        self._tick_handlers.append((pred, handler))

    @pyqtSlot(Tick)
    def _notify_tick_handlers(self, tick: Tick):
        tick_time = tick.time.time()

        for pred, handler in self._tick_handlers:
            if pred(tick_time):
                handler(tick)
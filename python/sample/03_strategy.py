import logging
import rmt
from time import sleep

class MyStrategy(rmt.Strategy):
    def __init__(self, exchange: rmt.Exchange):
        super().__init__(exchange, 'US100')

        self.bar_closed.connect(self._on_bar_closed)
        self.tick_received.connect(self._on_tick)

    def _on_bar_closed(self, bar: rmt.Bar):
        print('on_bar_closed:', self.instrument.symbol, bar)

    def _on_tick(self, tick: rmt.Tick):
        print('on_tick:', self.instrument.symbol, '-', tick)

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

exchange = rmt.exchanges.MetaTrader4()
strategy = MyStrategy(exchange)

for i in range(5):
    exchange.process_events()
    sleep(1)
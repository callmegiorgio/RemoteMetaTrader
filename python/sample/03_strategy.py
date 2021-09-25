import datetime
import logging
import rmt
from time import sleep

class MyStrategy(rmt.Strategy):
    def on_bar_closed(self, symbol: str, bar: rmt.Bar):
        print('on_bar_closed:', symbol, bar)

    def on_tick(self, symbol: str, server_time: datetime, bid: float, ask: float):
        print('on_tick:', symbol, server_time, bid, ask)

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

exchange = rmt.exchanges.MetaTrader4()
exchange.subscribe('US100')

strategy = MyStrategy(exchange)

for i in range(5):
    exchange.process_events()
    sleep(1)
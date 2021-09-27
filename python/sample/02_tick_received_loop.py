import logging
import rmt
from time import sleep

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

exchange = rmt.exchanges.MetaTrader4()
exchange.subscribe('US100')
exchange.subscribe('XAUUSD')
exchange.subscribe('EURUSD')

exchange.tick_received.connect(lambda symbol, tick: print(symbol, tick))

for i in range(10):
    exchange.process_events()
    sleep(1)
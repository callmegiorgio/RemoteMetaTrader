from time import sleep
import rmt
import logging

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

exchange = rmt.exchanges.MetaTrader4()

tick = exchange.get_tick('US100')
order = exchange.place_limit_order('US100', rmt.Side.SELL, 1, tick.bid + 1, 0, tick.bid - 2)

for i in range(5):
    print(exchange.get_tick('US100'))
    sleep(1)
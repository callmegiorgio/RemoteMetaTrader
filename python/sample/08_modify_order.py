from time import sleep
import rmt
import logging

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

exchange = rmt.exchanges.MetaTrader4()

tick = exchange.get_tick('US100')
order = exchange.place_limit_order('US100', rmt.Side.BUY, 1, tick.ask - 5)
print('order placed:', order)

print('sleeping for 3 seconds...')
sleep(3)

tick = exchange.get_tick('US100')
exchange.modify_order(order, order.stop_loss(), order.take_profit(), tick.ask - 3)
print('order modified:', order)
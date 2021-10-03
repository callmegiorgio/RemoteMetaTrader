from time import sleep
import rmt
import logging

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

exchange = rmt.exchanges.MetaTrader4()

tick = exchange.get_tick('US100')
ticket = exchange.place_order('US100', rmt.Side.BUY, rmt.OrderType.LIMIT_ORDER, 1, tick.ask - 5)
print('order placed:', ticket)

print('sleeping for 3 seconds...')
sleep(3)

tick = exchange.get_tick('US100')
exchange.modify_order(ticket, price=tick.ask - 3)
print('order modified:', ticket)
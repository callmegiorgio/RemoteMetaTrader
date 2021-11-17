from time import sleep
import rmt
import logging

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

exchange = rmt.exchanges.MetaTrader4()

tick = exchange.get_tick('US100')

ticket = exchange.place_order(
    symbol     = 'US100',
    side       = rmt.Side.BUY,
    order_type = rmt.OrderType.LIMIT_ORDER,
    lots       = 1,
    price      = tick.ask - 5,
    stop_loss  = tick.ask - 10
)

print('order placed:', ticket)

print('sleeping for 3 seconds...')
sleep(3)

tick = exchange.get_tick('US100')
exchange.modify_order(ticket, price=tick.ask - 3, stop_loss=None)
print('order modified:', ticket)
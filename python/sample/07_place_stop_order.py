from time import sleep
import rmt
import logging

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

exchange = rmt.exchanges.MetaTrader4()

tick = exchange.get_tick('US100')

ticket = exchange.place_order(
    symbol      = 'US100', 
    side        = rmt.Side.SELL,
    order_type  = rmt.OrderType.STOP_ORDER,
    lots        = 1,
    price       = tick.bid - 1,
    take_profit = tick.bid - 2
)

print('order placed:', ticket)
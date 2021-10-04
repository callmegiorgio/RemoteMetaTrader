from datetime import timedelta
import logging
import rmt

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

exchange1 = rmt.exchanges.MetaTrader4()
exchange2 = rmt.exchanges.MetaTrader4()

ticket = exchange1.place_order('US100', rmt.Side.BUY, rmt.OrderType.MARKET_ORDER, 1)

print('exchange1:')
print(exchange1.get_order(ticket))

print('exchange2:')
print(exchange2.get_order(ticket))
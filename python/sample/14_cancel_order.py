from time import sleep
import rmt
import logging

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

mt4 = rmt.exchanges.MetaTrader4()

symbol = 'US100'

us100 = mt4.get_instrument(symbol)
tick  = mt4.get_tick(symbol)

# Price at which a buy limit order will be filled: 100 points below the current bid price.
fill_price = tick.bid - round(us100.point * 100, us100.decimal_places)

ticket = mt4.place_order(
    symbol     = symbol,
    side       = rmt.Side.BUY,
    order_type = rmt.OrderType.LIMIT_ORDER,
    lots       = 1,
    price      = fill_price
)

order = mt4.get_order(ticket)

print('placed order #%s:' % ticket, order)

print('sleeping for 10 seconds...')
sleep(10)

mt4.cancel_order(ticket)

print('canceled order #%s:' % ticket, order)
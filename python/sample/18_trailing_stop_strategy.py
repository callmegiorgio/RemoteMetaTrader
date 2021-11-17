import logging
from rmt import exchanges, strategies, Side, OrderType, OrderStatus

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

mt4 = exchanges.MetaTrader4()
strategy = strategies.TrailingStopStrategy(mt4, 'US100')

# Fill order with SL starting at 2000 points "below" the current market price.
# At every move of 400 points on US100, reposition the SL by 100 points in
# the order's trend direction.
initial_sl_distance = 2000 * strategy.instrument.point
activation_distance = 400 * strategy.instrument.point
reposition_distance = 100 * strategy.instrument.point

# 2:1 profit-to-risk ratio.
tp_distance = initial_sl_distance * 2

tick = strategy.get_tick()

buy_order_ticket = strategy.place_order(
    side        = Side.BUY,
    order_type  = OrderType.MARKET_ORDER,
    price       = tick.ask,
    lots        = 0.1,
    stop_loss   = tick.ask - initial_sl_distance,
    take_profit = tick.ask + tp_distance
)

sell_order_ticket = strategy.place_order(
    side        = Side.SELL,
    order_type  = OrderType.MARKET_ORDER,
    price       = tick.bid,
    lots        = 0.1,
    stop_loss   = tick.bid + initial_sl_distance,
    take_profit = tick.bid - tp_distance
)

trailing_stop = strategies.SteadyTrailingStop(activation_distance, reposition_distance)

strategy.set_trailing_stop(buy_order_ticket, trailing_stop)
strategy.set_trailing_stop(sell_order_ticket, trailing_stop)

buy_order  = strategy.get_order(buy_order_ticket)
sell_order = strategy.get_order(sell_order_ticket)

while True:
    if (buy_order.status  == OrderStatus.CLOSED and
        sell_order.status == OrderStatus.CLOSED):
        print('Buy and sell orders closed. Bye!')
        break

    try:
        mt4.process_events()
    except Exception as e:
        print(str(e))

print(strategy.performance())
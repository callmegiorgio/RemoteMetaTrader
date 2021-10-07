import random, rmt
from time import sleep

def randomize_lots(min_lot: float, max_lot: float, lot_step: float) -> float:
    lots = random.uniform(min_lot, max_lot)
    
    lot_step_count = int(lots / lot_step)

    return lot_step_count * lot_step

mt4 = rmt.exchanges.MetaTrader4()
us100 = mt4.get_instrument('US100')

tickets = []
order_count = 5

print("I'mma fill %s orders cuz I'm comfident, hol' up" % order_count) # LMAO

for i in range(order_count):
    print('Filling order %s/%s in 10 seconds...' % (i + 1, order_count))
    
    sleep(10)

    lots = randomize_lots(us100.lot_step, 1, us100.lot_step)
    lots = round(lots, us100.decimal_places)

    ticket = mt4.place_order('US100', rmt.Side.BUY, rmt.OrderType.MARKET_ORDER, lots)
    tickets.append(ticket)
    
    print('Filled order #%s:' % ticket, mt4.get_order(ticket))

print('Waiting 15 seconds before closing orders...')
sleep(5)

print('10 seconds remaining...')
sleep(5)

print('5 seconds remaining...')
sleep(5)

orders = []

for ticket in tickets:
    mt4.close_order(ticket)

    order = mt4.get_order(ticket)
    orders.append(order)

    print('Closed order #%s:' % ticket, order)

    sleep(2)

print('Resulting performance:', rmt.Performance(orders, 2))
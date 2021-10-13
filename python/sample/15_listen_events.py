import logging
import rmt
import signal

logging.basicConfig()
logging.getLogger().setLevel(logging.WARNING)

def print_order(ticket: int, event_name: str):
    msg = '{1} order #{0}:'.format(ticket, event_name)

    print(msg, mt4.get_order(ticket))

mt4 = rmt.exchanges.MetaTrader4()
mt4.tick_received.connect(lambda symbol, tick: print('tick received:', symbol, '-', tick))
mt4.order_filled.connect(lambda ticket: print_order(ticket, 'filled'))
mt4.order_opened.connect(lambda ticket: print_order(ticket, 'opened'))
mt4.order_closed.connect(lambda ticket: print_order(ticket, 'closed'))
mt4.order_canceled.connect(lambda ticket: print_order(ticket, 'canceled'))
mt4.order_expired.connect(lambda ticket: print_order(ticket, 'expired'))
mt4.order_updated.connect(lambda ticket: print_order(ticket, 'updated'))

mt4.subscribe('US100')

signal.signal(signal.SIGINT, signal.SIG_DFL)

while True:
    mt4.process_events()
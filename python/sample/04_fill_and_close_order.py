from datetime import datetime
import rmt
import logging

class MyStrategy(rmt.Strategy):
    def __init__(self, exchange: rmt.Exchange):
        super().__init__(exchange, 'US100')

        self._done = False
        
        self.tick_received.connect(self._on_tick)

    def _on_tick(self, tick: rmt.Tick):
        print(self.instrument.symbol, '-', tick)

        if self._done:
            return

        active_orders = self.active_orders()
        
        if len(active_orders) == 0:
            ticket = self.place_order(
                side       = rmt.Side.BUY,
                order_type = rmt.OrderType.MARKET_ORDER,
                lots       = 1
            )

            print('filled order #{}'.format(ticket))
        else:
            ticket = active_orders.pop()

            self.close_order(ticket)
            
            print('closed order #{}'.format(ticket))

            self._done = True

    def is_done(self) -> bool:
        return self._done

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

exchange = rmt.exchanges.MetaTrader4()
strategy = MyStrategy(exchange)

while not strategy.is_done():
    exchange.process_events()
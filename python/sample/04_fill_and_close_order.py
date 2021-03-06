from datetime import datetime
import rmt
import logging

class MyStrategy(rmt.Strategy):
    def __init__(self, exchange: rmt.Exchange):
        super().__init__(exchange)

        self._last_order = None
        self._done = False

    def on_tick(self, symbol: str, server_time: datetime, bid: float, ask: float):
        print(symbol, server_time, bid, ask)

        if self._done:
            return

        if self._last_order is None:
            self._last_order = exchange.place_order(symbol, rmt.Side.BUY, rmt.OrderType.MARKET_ORDER, 1)
            print('filled order:', self._last_order)
        else:
            exchange.close_order(self._last_order)
            print('closed order:', self._last_order)
            self._done = True

    def is_done(self) -> bool:
        return self._done

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

exchange = rmt.exchanges.MetaTrader4()
exchange.subscribe('US100')

strategy = MyStrategy(exchange)

while not strategy.is_done():
    exchange.process_events()
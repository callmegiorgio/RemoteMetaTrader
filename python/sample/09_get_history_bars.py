from datetime import timedelta
import logging
import rmt

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

exchange = rmt.exchanges.MetaTrader4()

print('M1 bars:')
for bar in exchange.get_history_bars('US100'):
    print(bar)

print('H1 bars:')
for bar in exchange.get_history_bars('US100', timeframe=rmt.Timeframe.H1):
    print(bar)
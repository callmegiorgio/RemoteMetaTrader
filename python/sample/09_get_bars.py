from datetime import timedelta
import logging
import rmt

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

exchange = rmt.exchanges.MetaTrader4()

for bar in exchange.get_bars('US100'):
    print(bar)
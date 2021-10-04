from time import sleep
import logging
import rmt

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

exchange = rmt.exchanges.MetaTrader4()

for i in range(5):
    print(exchange.get_current_bar('US100'))
    sleep(1)
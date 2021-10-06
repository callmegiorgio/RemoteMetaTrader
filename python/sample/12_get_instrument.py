import rmt

mt4 = rmt.exchanges.MetaTrader4()

instrument = mt4.get_instrument('US100')

print(instrument)
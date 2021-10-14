from datetime import time
import logging, rmt, signal

logging.basicConfig()
logging.getLogger().setLevel(logging.WARNING)

mt4 = rmt.exchanges.MetaTrader4()
strategy = rmt.strategies.TimeBasedStrategy(mt4, 'US100')

# Invoke handler for 20 ticks after 11:30.
strategy.add_tick_handler(
    rmt.predicate.Count(rmt.predicate.AfterTime(hour=11, minute=30), count=20),
    lambda tick: print('tick after 11:30 ->', tick)
)

# Invoke handler for 15 ticks before 16:01.
strategy.add_tick_handler(
    rmt.predicate.Count(rmt.predicate.BeforeTime(hour=16, minute=1), count=15),
    lambda tick: print('tick before 16:01 ->', tick)
)

# Invoke handler for all ticks occuring at a time in range [17:22, 17:23).
strategy.add_tick_handler(
    rmt.predicate.TimeRange(
        time(hour=17, minute=22),
        time(hour=17, minute=23)
    ),
    lambda tick: print('tick within range [17:22, 17:23) ->', tick)
)

# Invoke handler for all ticks occuring at a time in ranges [23:58:37, midnight) and [midnight, 00:02:11).
strategy.add_tick_handler(
    rmt.predicate.TimeRange(
        time(hour=23, minute=58, second=37),
        time(hour=0, minute=2, second=11)
    ),
    lambda tick: print('tick within range [23:58:37, 00:02:11) ->', tick)
)

# Invoke handler for the first tick at 05:30.
strategy.add_tick_handler(
    rmt.predicate.Once(rmt.predicate.AtMinute(5, 30)),
    lambda tick: print('first tick at 05:30 ->', tick)
)

# Invoke handler for all ticks at 05:33.
strategy.add_tick_handler(
    rmt.predicate.AtMinute(5, 33),
    lambda tick: print('tick at 05:33 ->', tick)
)

# Invoke handler for all ticks at 10:33:30.
strategy.add_tick_handler(
    rmt.predicate.AtTime(hour=10, minute=33, second=30),
    lambda tick: print('tick at 10:33:30 ->', tick)
)

signal.signal(signal.SIGINT, signal.SIG_DFL)

while True:
    mt4.process_events()
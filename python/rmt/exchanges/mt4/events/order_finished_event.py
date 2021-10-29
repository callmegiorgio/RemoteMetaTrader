from datetime import datetime, timezone
from typing   import Optional
from .        import Event

class OrderFinishedEvent(Event):
    content_layout = {
        'ticket':     int,
        'opcode':     int,
        'cp':         float,
        'ct':         int,
        'sl':         (float, None),
        'tp':         (float, None),
        'expiration': (int,   None),
        'comment':    (str,   ''),
        'commission': (float, 0.0),
        'profit':     (float, 0.0),
        'swap':       (float, 0.0)
    }

    def ticket(self) -> int:
        return self['ticket']

    def opcode(self) -> int:
        return self['opcode']

    def close_price(self) -> float:
        return self['cp']

    def close_time(self) -> datetime:
        return datetime.fromtimestamp(self['ct'], timezone.utc)

    def stop_loss(self) -> Optional[float]:
        return self['sl']

    def take_profit(self) -> Optional[float]:
        return self['tp']

    def expiration(self) -> Optional[datetime]:
        expiration = self['expiration']

        if expiration is not None:
            expiration = datetime.fromtimestamp(expiration, timezone.utc)

        return expiration

    def comment(self) -> str:
        return self['comment']

    def commission(self) -> float:
        return self['commission']

    def profit(self) -> float:
        return self['profit']

    def swap(self) -> float:
        return self['swap']

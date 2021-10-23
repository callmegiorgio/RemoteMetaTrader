from datetime import datetime, timezone
from rmt import jsonutil, OrderStatus
from ..  import Content, OperationCode
from .   import Event

class OrderFinishedEvent(Event):
    content_layout = {
        'ticket':     int,
        'opcode':     int,
        'cp':         float,
        'ct':         int,
        'sl':         float,
        'tp':         float,
        'expiration': int,
        'comment':    (str, ''),
        'commission': float,
        'profit':     float,
        'swap':       float
    }

    def ticket(self) -> int:
        return self['ticket']

    def opcode(self) -> int:
        return self['opcode']

    def close_price(self) -> float:
        return self['cp']

    def close_time(self) -> datetime:
        return datetime.fromtimestamp(self['ct'], timezone.utc)

    def stop_loss(self) -> float:
        return self['sl']

    def take_profit(self) -> float:
        return self['tp']

    def expiration(self) -> datetime:
        return datetime.fromtimestamp(self['expiration'], timezone.utc)

    def comment(self) -> str:
        return self['comment']

    def commission(self) -> float:
        return self['commission']

    def profit(self) -> float:
        return self['profit']

    def swap(self) -> float:
        return self['swap']

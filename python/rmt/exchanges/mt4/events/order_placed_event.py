from datetime import datetime, timezone
from .        import Event

class OrderPlacedEvent(Event):    
    content_layout = {
        'opcode':     int,
        'ticket':     int,
        'symbol':     str,
        'lots':       float,
        'op':         float,
        'ot':         int,
        'sl':         float,
        'tp':         float,
        'expiration': int,
        'magic':      (int, 0),
        'comment':    (str, ''),
        'commission': float,
        'profit':     float,
        'swap':       float
    }

    def opcode(self) -> int:
        return self['opcode']

    def ticket(self) -> int:
        return self['ticket']

    def symbol(self) -> str:
        return self['symbol']

    def lots(self) -> float:
        return self['lots']

    def open_price(self) -> float:
        return self['op']

    def open_time(self) -> datetime:
        return datetime.fromtimestamp(self['ot'], timezone.utc)

    def stop_loss(self) -> float:
        return self['sl']

    def take_profit(self) -> float:
        return self['tp']

    def expiration(self) -> datetime:
        return datetime.fromtimestamp(self['expiration'], timezone.utc)

    def magic_number(self) -> int:
        return self['magic']

    def comment(self) -> str:
        return self['comment']

    def commission(self) -> float:
        return self['commission']

    def profit(self) -> float:
        return self['profit']

    def swap(self) -> float:
        return self['swap']
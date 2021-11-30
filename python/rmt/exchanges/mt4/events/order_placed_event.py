from typing import Optional
from .      import Event

class OrderPlacedEvent(Event):    
    content_layout = {
        'opcode':     int,
        'ticket':     int,
        'symbol':     str,
        'lots':       float,
        'op':         float,
        'ot':         str,
        'sl':         (float, None),
        'tp':         (float, None),
        'expiration': (str,   None),
        'magic':      (int,   0),
        'comment':    (str,   ''),
        'commission': (float, 0.0),
        'profit':     (float, 0.0),
        'swap':       (float, 0.0)
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

    def open_time(self) -> str:
        return self['ot']

    def stop_loss(self) -> Optional[float]:
        return self['sl']

    def take_profit(self) -> Optional[float]:
        return self['tp']

    def expiration(self) -> Optional[str]:
        return self['expiration']

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
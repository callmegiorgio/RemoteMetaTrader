from typing import Optional
from .      import Response

class GetOrder(Response):
    content_layout = {
        'opcode':     int,
        'status':     str,
        'symbol':     str,
        'lots':       float,
        'op':         float,
        'ot':         int,
        'cp':         (int,   None),
        'ct':         (int,   None),
        'sl':         (float, None),
        'tp':         (float, None),
        'expiration': (int,   None),
        'comment':    (str,   ''),
        'magic':      (int,   0),
        'commission': float,
        'profit':     float,
        'swap':       float
    }

    def opcode(self) -> int:
        return self['opcode']

    def status(self) -> str:
        return self['status']

    def symbol(self) -> str:
        return self['symbol']

    def lots(self) -> float:
        return self['lots']

    def open_price(self) -> float:
        return self['op']

    def open_time(self) -> int:
        return self['ot']

    def close_price(self) -> Optional[float]:
        return self['cp']

    def close_time(self) -> Optional[int]:
        return self['ct']

    def stop_loss(self) -> Optional[float]:
        return self['sl']

    def take_profit(self) -> Optional[float]:
        return self['tp']

    def expiration(self) -> Optional[int]:
        return self['expiration']

    def comment(self) -> str:
        return self['comment']

    def magic_number(self) -> int:
        return self['magic']

    def commission(self) -> float:
        return self['commission']

    def profit(self) -> float:
        return self['profit']

    def swap(self) -> float:
        return self['swap']
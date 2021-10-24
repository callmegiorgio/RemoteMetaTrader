from datetime import datetime, timezone
from typing   import Optional
from .        import Response

class PlaceOrder(Response):
    content_layout = {
        'ticket':     int,
        'lots':       (float, None),
        'op':         (float, None),
        'ot':         (int,   None),
        'commission': (float, None),
        'profit':     (float, None),
        'swap':       (float, None)
    }   

    def ticket(self) -> int:
        return self['ticket']

    def lots(self) -> Optional[float]:
        return self['lots']

    def open_price(self) -> Optional[float]:
        return self['op']

    def open_time(self) -> Optional[datetime]:
        return datetime.fromtimestamp(self['ot'], timezone.utc)

    def commission(self) -> Optional[float]:
        return self['commission']

    def profit(self) -> Optional[float]:
        return self['profit']

    def swap(self) -> Optional[float]:
        return self['swap']
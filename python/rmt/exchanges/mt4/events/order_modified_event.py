from datetime import datetime, timezone
from .        import Event

class OrderModifiedEvent(Event):
    content_layout = {
        'ticket':     int,
        'op':         float,
        'sl':         float,
        'tp':         float,
        'expiration': int
    }

    def ticket(self) -> int:
        return self['ticket']

    def open_price(self) -> float:
        return self['op']

    def stop_loss(self) -> float:
        return self['sl']

    def take_profit(self) -> float:
        return self['tp']

    def expiration(self) -> datetime:
        return datetime.fromtimestamp(self['expiration'], timezone.utc)

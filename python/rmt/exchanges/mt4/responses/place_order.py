from datetime import datetime, timezone
from typing   import Dict
from rmt      import jsonutil
from ..       import Content

class PlaceOrderResponse:
    def __init__(self, content: Content):
        self._ticket     = jsonutil.read_required(content, 'ticket',     int)
        self._lots       = jsonutil.read_required(content, 'lots',       float)
        self._open_price = jsonutil.read_required(content, 'op',         float)
        open_timestamp   = jsonutil.read_required(content, 'ot',         int)
        self._commission = jsonutil.read_required(content, 'commission', float)
        self._profit     = jsonutil.read_required(content, 'profit',     float)
        self._swap       = jsonutil.read_required(content, 'swap',       float)

        self._open_time = datetime.fromtimestamp(open_timestamp, timezone.utc)
    
    def ticket(self) -> int:
        return self._ticket

    def lots(self) -> float:
        return self._lots

    def open_price(self) -> float:
        return self._open_price

    def open_time(self) -> datetime:
        return self._open_time

    def commission(self) -> float:
        return self._commission

    def profit(self) -> float:
        return self._profit

    def swap(self) -> float:
        return self._swap
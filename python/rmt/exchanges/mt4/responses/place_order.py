from datetime   import datetime, timezone
from typing     import Dict
from rmt        import jsonutil
from ..requests import PlaceOrderRequest
from .          import Response

class PlaceOrderResponse(Response):
    command = PlaceOrderRequest.command

    def deserialize(self, obj: Dict):
        self._ticket     = jsonutil.read_required_key(obj, 'ticket', int)
        self._lots       = jsonutil.read_optional(obj, 'lots', float)
        self._open_price = jsonutil.read_optional(obj, 'op', float)
        open_timestamp   = jsonutil.read_optional(obj, 'ot',         int)
        self._commission = jsonutil.read_optional(obj, 'commission', float)
        self._profit     = jsonutil.read_optional(obj, 'profit',     float)
        self._swap       = jsonutil.read_optional(obj, 'swap',       float)

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
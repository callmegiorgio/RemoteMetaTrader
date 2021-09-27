from datetime   import datetime, timezone
from typing     import Dict
from rmt        import jsonutil
from ..requests import CloseOrderRequest
from .          import Response

class CloseOrderResponse(Response):
    command = CloseOrderRequest.command

    def deserialize(self, obj: Dict):
        self._lots        = jsonutil.read_optional(obj, 'lots',       float)
        self._close_price = jsonutil.read_optional(obj, 'cp',         float)
        close_timestamp   = jsonutil.read_optional(obj, 'ct',         int)
        self._comment     = jsonutil.read_optional(obj, 'comment',    str)
        self._commission  = jsonutil.read_optional(obj, 'commission', float)
        self._profit      = jsonutil.read_optional(obj, 'profit',     float)
        self._swap        = jsonutil.read_optional(obj, 'swap',       float)

        self._close_time = datetime.fromtimestamp(close_timestamp, timezone.utc)

    def lots(self) -> float:
        return self._lots

    def close_price(self) -> float:
        return self._close_price

    def close_time(self) -> datetime:
        return self._close_time

    def comment(self) -> str:
        return self._comment

    def commission(self) -> float:
        return self._commission

    def profit(self) -> float:
        return self._profit

    def swap(self) -> float:
        return self._swap
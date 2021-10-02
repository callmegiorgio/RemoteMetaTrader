from datetime import datetime, timezone
from typing   import Dict, Optional
from rmt      import jsonutil
from ..       import Content

class CloseOrderResponse:
    class NewOrder:
        def __init__(self, obj: Dict):
            self._ticket       = jsonutil.read_required(obj, 'ticket',     int)
            self._lots         = jsonutil.read_optional(obj, 'lots',       float)
            self._magic_number = jsonutil.read_optional(obj, 'magic',      int)
            self._comment      = jsonutil.read_optional(obj, 'comment',    str)
            self._commission   = jsonutil.read_optional(obj, 'commission', float)
            self._profit       = jsonutil.read_optional(obj, 'profit',     float)
            self._swap         = jsonutil.read_optional(obj, 'swap',       float)

        def ticket(self) -> int:
            return self._ticket
        
        def lots(self) -> float:
            return self._lots

        def magic_number(self) -> int:
            return self._magic_number
            
        def comment(self) -> str:
            return self._comment
            
        def commission(self) -> float:
            return self._commission
            
        def profit(self) -> float:
            return self._profit
            
        def swap(self) -> float:
            return self._swap

    def __init__(self, content: Content):
        self._lots        = jsonutil.read_optional(content, 'lots',       float)
        self._close_price = jsonutil.read_optional(content, 'cp',         float)
        close_timestamp   = jsonutil.read_optional(content, 'ct',         int)
        self._comment     = jsonutil.read_optional(content, 'comment',    str)
        self._commission  = jsonutil.read_optional(content, 'commission', float)
        self._profit      = jsonutil.read_optional(content, 'profit',     float)
        self._swap        = jsonutil.read_optional(content, 'swap',       float)

        self._close_time = datetime.fromtimestamp(close_timestamp, timezone.utc)

        new_order_obj = jsonutil.read_optional(content, 'new_order', dict)

        if len(new_order_obj) != 0:
            self._new_order = CloseOrderResponse.NewOrder(new_order_obj)
        else:
            self._new_order = None

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

    def new_order(self) -> Optional[NewOrder]:
        return self._new_order
from datetime import datetime, timezone
from rmt      import jsonutil
from ..       import Content

class CloseOrderResponse:
    def __init__(self, content: Content):
        self._lots        = jsonutil.read_required(content, 'lots',       float)
        self._close_price = jsonutil.read_required(content, 'cp',         float)
        close_timestamp   = jsonutil.read_required(content, 'ct',         int)
        self._comment     = jsonutil.read_required(content, 'comment',    str)
        self._commission  = jsonutil.read_required(content, 'commission', float)
        self._profit      = jsonutil.read_required(content, 'profit',     float)
        self._swap        = jsonutil.read_required(content, 'swap',       float)

        self._close_time = datetime.fromtimestamp(close_timestamp, timezone.utc)

        new_order = jsonutil.read_optional(content, 'new_order', dict)

        if len(new_order) != 0:
            self._new_order_ticket       = jsonutil.read_required(new_order, 'ticket',     int)
            self._new_order_lots         = jsonutil.read_required(new_order, 'lots',       float)
            self._new_order_magic_number = jsonutil.read_required(new_order, 'magic',      int)
            self._new_order_comment      = jsonutil.read_required(new_order, 'comment',    str)
            self._new_order_commission   = jsonutil.read_required(new_order, 'commission', float)
            self._new_order_profit       = jsonutil.read_required(new_order, 'profit',     float)
            self._new_order_swap         = jsonutil.read_required(new_order, 'swap',       float)
        else:
            self._new_order_ticket       = int(0)
            self._new_order_lots         = float(0)
            self._new_order_magic_number = int(0)
            self._new_order_comment      = ''
            self._new_order_commission   = float(0)
            self._new_order_profit       = float(0)
            self._new_order_swap         = float(0)

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

    def new_order_ticket(self) -> int:
        return self._new_order_ticket
        
    def new_order_lots(self) -> float:
        return self._new_order_lots

    def new_order_magic_number(self) -> int:
        return self._new_order_magic_number
        
    def new_order_comment(self) -> str:
        return self._new_order_comment
        
    def new_order_commission(self) -> float:
        return self._new_order_commission
        
    def new_order_profit(self) -> float:
        return self._new_order_profit
        
    def new_order_swap(self) -> float:
        return self._new_order_swap
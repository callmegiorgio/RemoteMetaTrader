from typing     import Dict
from rmt        import jsonutil
from ..requests import PartialCloseOrderRequest
from .          import CloseOrderResponse

class PartialCloseOrderResponse(CloseOrderResponse):
    command = PartialCloseOrderRequest.command

    def deserialize(self, obj: Dict):
        super().deserialize(obj)

        rem_order = jsonutil.read_optional(obj, 'remaining_order', dict)

        self._remaining_order_ticket       = jsonutil.read_optional(rem_order, 'ticket',     int)
        self._remaining_order_lots         = jsonutil.read_optional(rem_order, 'lots',       float)
        self._remaining_order_magic_number = jsonutil.read_optional(rem_order, 'magic',      int)
        self._remaining_order_comment      = jsonutil.read_optional(rem_order, 'comment',    str)
        self._remaining_order_commission   = jsonutil.read_optional(rem_order, 'commission', float)
        self._remaining_order_profit       = jsonutil.read_optional(rem_order, 'profit',     float)
        self._remaining_order_swap         = jsonutil.read_optional(rem_order, 'swap',       float)

    def remaining_order_ticket(self) -> int:
        return self._remaining_order_ticket
        
    def remaining_order_lots(self) -> float:
        return self._remaining_order_lots

    def remaining_order_magic_number(self) -> int:
        return self._remaining_order_magic_number
        
    def remaining_order_comment(self) -> str:
        return self._remaining_order_comment
        
    def remaining_order_commission(self) -> float:
        return self._remaining_order_commission
        
    def remaining_order_profit(self) -> float:
        return self._remaining_order_profit
        
    def remaining_order_swap(self) -> float:
        return self._remaining_order_swap
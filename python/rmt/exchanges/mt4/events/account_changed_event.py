from rmt import jsonutil
from ..  import Content
from .   import Event

class AccountChangedEvent(Event):
    def __init__(self, dynamic_name: str, content: Content):
        if not isinstance(content, dict):
            raise ValueError("account changed event content is of invalid type (expected: object, got: array)")

        self._currency          = jsonutil.read_required(content, 'currency',        str)
        self._leverage          = jsonutil.read_required(content, 'leverage',        int)
        self._credit            = jsonutil.read_required(content, 'credit',          float)
        self._expert_allowed    = jsonutil.read_required(content, 'expertAllowed',   float)
        self._trade_allowed     = jsonutil.read_required(content, 'tradeAllowed',    float)
        self._max_active_orders = jsonutil.read_required(content, 'maxActiveOrders', float)

    def currency(self) -> str:
        return self._currency

    def leverage(self) -> int:
        return self._leverage

    def credit(self) -> float:
        return self._credit

    def is_expert_allowed(self) -> float:
        return self._expert_allowed

    def is_trade_allowed(self) -> float:
        return self._trade_allowed

    def max_active_orders(self) -> float:
        return self._max_active_orders
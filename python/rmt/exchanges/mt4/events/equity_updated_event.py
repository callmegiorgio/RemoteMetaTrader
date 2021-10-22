from typing import Optional
from rmt    import jsonutil
from ..     import Content
from .      import Event

class EquityUpdatedEvent(Event):
    def __init__(self, dynamic_name: str, content: Content):
        if not isinstance(content, dict):
            raise ValueError("equity updated event content is of invalid type (expected: object, got: array)")

        self._equity      = jsonutil.read_required(content, 'equity',     float)
        self._profit      = jsonutil.read_required(content, 'profit',     float)
        self._margin      = jsonutil.read_required(content, 'margin',     float)
        self._margin_lvl  = jsonutil.read_required(content, 'marginLvl',  float)
        self._free_margin = jsonutil.read_required(content, 'freeMargin', float)
        self._balance     = jsonutil.read_optional(content, 'balance',    float, None)

    def equity(self) -> float:
        return self._equity

    def profit(self) -> float:
        return self._profit

    def margin(self) -> float:
        return self._margin
    
    def margin_level(self) -> float:
        return self._margin_lvl

    def free_margin(self) -> float:
        return self._free_margin
    
    def balance(self) -> Optional[float]:
        return self._balance
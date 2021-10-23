from typing import Optional
from .      import Event

class EquityUpdatedEvent(Event):
    content_layout = {
        'equity':     float,
        'profit':     float,
        'margin':     float,
        'marginLvl':  float,
        'freeMargin': float,
        'balance':    (float, None)
    }

    def equity(self) -> float:
        return self['equity']

    def profit(self) -> float:
        return self['profit']

    def margin(self) -> float:
        return self['margin']
    
    def margin_level(self) -> float:
        return self['marginLvl']

    def free_margin(self) -> float:
        return self['freeMargin']
    
    def balance(self) -> Optional[float]:
        return self['balance']
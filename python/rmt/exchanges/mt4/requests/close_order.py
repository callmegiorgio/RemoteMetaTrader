from typing import Dict
from .      import Request

class CloseOrderRequest(Request):
    command = 'close_order'

    def __init__(self,
                 ticket: int,
                 price: float,
                 slippage: int,
                 lots: float
    ):
        super().__init__()

        self._ticket   = ticket
        self._price    = price
        self._slippage = slippage
        self._lots     = lots

    def message(self) -> Dict:
        return {
            'ticket':   self._ticket,
            'lots':     self._lots,
            'price':    self._price,
            'slippage': self._slippage
        }
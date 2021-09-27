from typing import Dict
from .      import Request

class CloseOrderRequest(Request):
    command = 'close_order'

    def __init__(self,
                 ticket: int,
                 price: float,
                 slippage: int
    ):
        super().__init__()

        self._ticket   = ticket
        self._price    = price
        self._slippage = slippage

    def message(self) -> Dict:
        msg = {
            'ticket': self._ticket
        }

        if self._price != 0:
            msg['price'] = self._price

        if self._slippage != 0:
            msg['slippage'] = self._slippage

        return msg
from typing import Optional
from ..     import Content
from .      import Request

class CloseOrderRequest(Request):
    command = 'closeOrder'

    def __init__(self,
                 ticket:   int,
                 price:    Optional[float],
                 slippage: int,
                 lots:     Optional[float]
    ):
        super().__init__()

        self._ticket   = ticket
        self._lots     = lots
        self._price    = price
        self._slippage = slippage

    def content(self) -> Content:
        msg = {
            'ticket': self._ticket
        }

        if self._price is not None:
            msg['price'] = float(self._price)

        if self._slippage != 0:
            msg['slippage'] = self._slippage

        if self._lots is not None:
            msg['lots'] = float(self._lots)

        return msg
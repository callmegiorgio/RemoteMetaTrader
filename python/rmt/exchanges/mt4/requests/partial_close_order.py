from typing import Dict
from .      import CloseOrderRequest

class PartialCloseOrderRequest(CloseOrderRequest):
    command = 'pclose_order'

    def __init__(self,
                 ticket: int,
                 lots: float,
                 price: float,
                 slippage: int
    ):
        super().__init__(ticket, price, slippage)

        if lots == 0:
            raise ValueError("order cannot be closed with a 'lots' value of 0")

        self._lots = lots

    def message(self) -> Dict:
        msg = super().message()

        msg['lots'] = self._lots

        return msg
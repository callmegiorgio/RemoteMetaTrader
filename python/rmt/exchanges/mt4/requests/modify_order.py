from datetime import datetime
from typing   import Optional
from ..       import Content
from .        import Request

class ModifyOrderRequest(Request):
    command = 'modifyOrder'

    def __init__(self,
                 ticket:      int,
                 stop_loss:   Optional[float],
                 take_profit: Optional[float],
                 price:       Optional[float],
                 expiration:  Optional[datetime]
    ):
        super().__init__()

        self._ticket      = ticket
        self._stop_loss   = stop_loss
        self._take_profit = take_profit
        self._price       = price
        self._expiration  = expiration

    def content(self) -> Content:
        msg = {
            'ticket': self._ticket
        }

        if self._stop_loss is not None:
            msg['sl'] = float(self._stop_loss)

        if self._take_profit is not None:
            msg['tp'] = float(self._take_profit)

        if self._price is not None:
            msg['price'] = float(self._price)

        if self._expiration is not None:
            msg['expiration'] = int(self._expiration.timestamp())

        return msg
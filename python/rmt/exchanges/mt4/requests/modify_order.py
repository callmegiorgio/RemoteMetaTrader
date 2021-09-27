from datetime import datetime
from typing   import Dict, Optional
from .        import Request

class ModifyOrderRequest(Request):
    command = 'modify_order'

    def __init__(self,
                 ticket: int,
                 stop_loss: float,
                 take_profit: float,
                 price: Optional[float],
                 expiration: Optional[datetime]
    ):
        super().__init__()

        self._ticket      = ticket
        self._stop_loss   = stop_loss
        self._take_profit = take_profit
        self._price       = price
        self._expiration  = expiration

    def message(self) -> Dict:
        msg = {
            'ticket': self._ticket,
            'sl':     self._stop_loss,
            'tp':     self._take_profit
        }

        if self._price is not None:
            msg['price'] = float(self._price)

        if self._expiration is not None:
            msg['expiration'] = int(self._expiration.timestamp())

        return msg
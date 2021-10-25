from datetime import datetime
from typing   import Optional
from ..       import OperationCode, Content
from .        import Request

class PlaceOrder(Request):
    command = 'placeOrder'

    def __init__(self,
                 symbol:       str,
                 opcode:       OperationCode,
                 lots:         float,
                 price:        Optional[float],
                 slippage:     Optional[int],
                 stop_loss:    Optional[float],
                 take_profit:  Optional[float],
                 comment:      str,
                 magic_number: int,
                 expiration:   Optional[datetime]
    ):
        super().__init__()

        self._symbol       = symbol
        self._opcode       = opcode
        self._lots         = lots
        self._price        = price
        self._slippage     = slippage
        self._stop_loss    = stop_loss
        self._take_profit  = take_profit
        self._comment      = comment
        self._magic_number = magic_number
        self._expiration   = expiration

    def content(self) -> Content:
        msg = {
            'symbol': self._symbol,
            'opcode': self._opcode.value,
            'lots':   self._lots
        }

        if self._price is not None:
            msg['price'] = float(self._price)

        if self._slippage is not None:
            msg['slippage'] = int(self._slippage)

        if self._stop_loss is not None:
            msg['sl'] = float(self._stop_loss)
        
        if self._take_profit is not None:
            msg['tp'] = float(self._take_profit)

        if self._comment != '':
            msg['comment'] = self._comment

        if self._magic_number != 0:
            msg['magic'] = self._magic_number

        if self._expiration is not None:
            msg['expiration'] = int(self._expiration.timestamp())

        return msg
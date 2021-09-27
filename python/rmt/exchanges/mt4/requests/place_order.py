from datetime import datetime
from typing   import Dict, Optional
from ..       import OperationCode
from .        import Request

class PlaceOrderRequest(Request):
    command = 'place_order'

    def __init__(
        self,
        symbol: str,
        opcode: OperationCode,
        lots: float,
        price: float,
        slippage: int,
        stop_loss: float,
        take_profit: float,
        comment: str,
        magic_number: int,
        expiration: Optional[datetime]
    ):
        super().__init__()

        if symbol == '':
            raise ValueError('symbol must not be empty')

        if price == 0 and (opcode not in [OperationCode.BUY, OperationCode.SELL]):
            raise ValueError('pending order price cannot be zero')

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

    def message(self) -> Dict:
        msg = {
            'symbol': self._symbol,
            'opcode': self._opcode.value,
            'lots':   self._lots
        }

        if self._price != 0:
            msg['price'] = self._price

        if self._slippage != 0:
            msg['slippage'] = self._slippage

        if self._stop_loss != 0.0:
            msg['sl'] = self._stop_loss
        
        if self._take_profit != 0.0:
            msg['tp'] = self._take_profit

        if self._comment != '':
            msg['comment'] = self._comment

        if self._magic_number != 0:
            msg['magic'] = self._magic_number
        
        if isinstance(self._expiration, datetime):
            msg['expiration'] = int(self._expiration.timestamp())

        return msg
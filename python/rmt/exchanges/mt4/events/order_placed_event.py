from datetime import datetime
from rmt import jsonutil, Order, Side, OrderType, OrderStatus
from ..  import Content, OperationCode
from .   import Event

class OrderPlacedEvent(Event):
    def __init__(self, dynamic_name: str, content: Content):
        if not isinstance(content, dict):
            raise ValueError("order event content is of invalid type (expected: object, got: array)")

        opcode = jsonutil.read_required(content, 'opcode', int)
        opcode = OperationCode(opcode)

        side       = None
        order_type = None
        status     = None

        if opcode in [OperationCode.BUY, OperationCode.SELL]:
            side       = Side.BUY if opcode == OperationCode.BUY else Side.SELL
            order_type = OrderType.MARKET_ORDER
            status     = OrderStatus.FILLED

        elif opcode in [OperationCode.BUY_LIMIT, OperationCode.SELL_LIMIT]:
            side       = Side.BUY if opcode == OperationCode.BUY_LIMIT else Side.SELL
            order_type = OrderType.LIMIT_ORDER
            status     = OrderStatus.PENDING

        else:
            side       = Side.BUY if opcode == OperationCode.BUY_STOP else Side.SELL
            order_type = OrderType.STOP_ORDER
            status     = OrderStatus.PENDING
        
        self._order = Order(
            ticket       = jsonutil.read_required(content, 'ticket', int),
            symbol       = jsonutil.read_required(content, 'symbol', str),
            side         = side,
            type         = order_type,
            lots         = jsonutil.read_required(content, 'lots', float),
            status       = status,
            open_price   = jsonutil.read_required(content, 'op',         float),
            open_time    = jsonutil.read_required(content, 'ot',         datetime),
            stop_loss    = jsonutil.read_required(content, 'sl',         float),
            take_profit  = jsonutil.read_required(content, 'tp',         float),
            expiration   = jsonutil.read_required(content, 'expiration', datetime),
            magic_number = jsonutil.read_optional(content, 'magic',      int),
            comment      = jsonutil.read_optional(content, 'comment',    str),
            commission   = jsonutil.read_required(content, 'commission', float),
            profit       = jsonutil.read_required(content, 'profit',     float),
            swap         = jsonutil.read_required(content, 'swap',       float)
        )

    def order(self) -> Order:
        return self._order
from datetime import datetime
from typing   import Optional
from rmt      import jsonutil, Side, Order, OrderType, OrderStatus
from ..       import Content, OperationCode

class GetOrderResponse:
    def __init__(self, ticket: int, content: Content):
        opcode       = self._read_opcode(content)
        status       = self._read_status(content)
        symbol       = jsonutil.read_required(content, 'symbol',     str)
        lots         = jsonutil.read_required(content, 'lots',       float)
        open_price   = jsonutil.read_required(content, 'op',         float)
        open_time    = jsonutil.read_required(content, 'ot',         datetime)
        close_price  = self._read_close_price(content, status)
        close_time   = self._read_close_time (content, status)
        stop_loss    = jsonutil.read_optional(content, 'sl',         float,    None)
        take_profit  = jsonutil.read_optional(content, 'tp',         float,    None)
        expiration   = jsonutil.read_optional(content, 'expiration', datetime, None)
        comment      = jsonutil.read_optional(content, 'comment',    str,      '')
        magic_number = jsonutil.read_optional(content, 'magic',      int,      0)
        commission   = jsonutil.read_required(content, 'commission', float)
        profit       = jsonutil.read_required(content, 'profit',     float)
        swap         = jsonutil.read_required(content, 'swap',       float)

        side       = None
        order_type = None

        if opcode in [OperationCode.BUY, OperationCode.SELL]:
            side       = Side.BUY if opcode == OperationCode.BUY else Side.SELL
            order_type = OrderType.MARKET_ORDER
        elif opcode in [OperationCode.BUY_LIMIT, OperationCode.SELL_LIMIT]:
            side       = Side.BUY if opcode == OperationCode.BUY_LIMIT else Side.SELL
            order_type = OrderType.LIMIT_ORDER
        else:
            side       = Side.BUY if opcode == OperationCode.BUY_STOP else Side.SELL
            order_type = OrderType.STOP_ORDER

        self._order = Order(
            ticket       = ticket,
            symbol       = symbol,
            side         = side,
            type         = order_type,
            lots         = lots,
            status       = status,
            open_price   = open_price,
            open_time    = open_time,
            close_price  = close_price,
            close_time   = close_time,
            stop_loss    = stop_loss,
            take_profit  = take_profit,
            expiration   = expiration,
            magic_number = magic_number,
            comment      = comment,
            commission   = commission,
            profit       = profit,
            swap         = swap
        )

    def _read_opcode(self, content: Content) -> OperationCode:
        opcode = jsonutil.read_required(content, 'opcode', int)

        is_valid_opcode = any(opcode == o.value for o in OperationCode)

        if not is_valid_opcode:
            raise ValueError("invalid operation code %s" % opcode)

        return OperationCode(opcode)

    def _read_status(self, content: Content) -> OrderStatus:
        status = jsonutil.read_required(content, 'status', str)
        
        if   status == 'pending':  status = OrderStatus.PENDING
        elif status == 'filled':   status = OrderStatus.FILLED
        elif status == 'canceled': status = OrderStatus.CANCELED
        elif status == 'expired':  status = OrderStatus.EXPIRED
        elif status == 'closed':   status = OrderStatus.CLOSED
        else:
            raise ValueError("invalid order status '%s'" % status)

        return status

    def _read_close_price(self, content: Content, status: OrderStatus) -> Optional[float]:
        if status == OrderStatus.CLOSED:
            return jsonutil.read_required(content, 'cp', float)
        else:
            return None

    def _read_close_time(self, content: Content, status: OrderStatus) -> Optional[datetime]:
        if status == OrderStatus.CLOSED:
            return jsonutil.read_required(content, 'ct', datetime)
        else:
            return None

    def order(self) -> Order:
        return self._order
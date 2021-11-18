from typing import Any, Optional, Type
from rmt    import Side, OrderType

class RMTError(Exception):
    pass

class NotImplementedException(RMTError):
    """Raised if a method is not implemented."""

    def __init__(self, class_type: Type[Any], method_name: str):
        error_msg = 'method {1} of class {0} is not implemented'.format(class_type, method_name)

        super().__init__(error_msg)

class RequestError(RMTError):
    """Raised if an error occurs before execution of an order."""

    pass

class RequestTimeout(RequestError):
    """Raised if an exchange takes too long to reply to a request."""

    pass

class ExecutionError(RMTError):
    """Raised if an error occurs during execution of an order."""

    pass

class ConnectionLost(ExecutionError):
    """Raised if connection to trade server is lost."""

    pass

class InvalidSymbol(ExecutionError):
    """Raised if a symbol does not identify an instrument."""

    def __init__(self, symbol: str):
        error_msg = 'no instrument found with symbol {}'.format(symbol)

        super().__init__(error_msg)

    pass

class OffQuotes(ExecutionError):
    """Raised if place order request breaches a limit set by an exchange."""

    def __init__(self, symbol: str, side: Side, order_type: OrderType):
        symbol     = str(symbol)
        side       = side.name.lower()                         # 'buy' or 'sell'
        order_type = order_type.name.lower().replace('_', ' ') # 'market order', 'limit order', or 'stop order'

        error_msg = (
            "cannot place {1} {2} at given price for instrument '{0}'"
            .format(symbol, side, order_type)
        )

        super().__init__(error_msg)

class Requote(ExecutionError):
    """Raised if a market order is requested to be filled at an outdated price."""

    def __init__(self, symbol: str):
        symbol = str(symbol)

        error_msg = (
            "price has become out of date for instrument '{}', or bid and ask prices have been mixed up"
            .format(symbol)
        )

        super().__init__(error_msg)

class InvalidTicket(ExecutionError):
    """Raised if a ticket number does not identify an order."""

    def __init__(self, ticket: int):
        error_msg = 'no order found with ticket number ' + str(ticket)

        super().__init__(error_msg)

class InvalidOrderStatus(ExecutionError):
    """Raised if status of an order is invalid for a requested operation."""

    def __init__(self, status: str):
        # TODO: print operation name and order's ticket
        error_msg = "invalid order status '{}' for operation".format(status)

        super().__init__(error_msg)

class ExchangeRateError(ExecutionError):
    """Raised if no exchange rate is found for a currency pair."""

    def __init__(self, base_currency: str, quote_currency: str):
        error_msg = "no exchange rate found for currency pair {0}/{1}".format(base_currency, quote_currency)

        super().__init__(error_msg)

class InvalidStops(ExecutionError):
    """Raised if a Stop Loss or Take Profit price is invalid."""

    def __init__(self, stop_loss: Optional[float], take_profit: Optional[float]):
        error_msg = (
            'either Stop Loss ({0}) or Take Profit ({1}) is invalid'
            .format(stop_loss, take_profit)
        )

        super().__init__(error_msg)
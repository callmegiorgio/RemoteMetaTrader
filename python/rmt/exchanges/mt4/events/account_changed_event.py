from . import Event

class AccountChangedEvent(Event):
    content_layout = {
        'currency':        str,
        'leverage':        int,
        'credit':          float,
        'expertAllowed':   float,
        'tradeAllowed':    float,
        'maxActiveOrders': float
    }

    def currency(self) -> str:
        return self['currency']

    def leverage(self) -> int:
        return self['leverage']

    def credit(self) -> float:
        return self['credit']

    def is_expert_allowed(self) -> float:
        return self['expertAllowed']

    def is_trade_allowed(self) -> float:
        return self['tradeAllowed']

    def max_active_orders(self) -> float:
        return self['maxActiveOrders']
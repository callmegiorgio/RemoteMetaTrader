from . import Response

class GetAccount(Response):
    content_layout = {
        'login':      int,
        'name':       str,
        'server':     str,
        'company':    str,
        'mode':       str,
        'leverage':   int,
        'orderLimit': int,
        'currency':   str,
        'balance':    float,
        'credit':     float,
        'profit':     float,
        'equity':     float,
        'margin':     float,
        'freeMargin': float,
        'marginLvl':  float,
        'canTrade':   bool,
        'canExpert':  bool
    }

    def login(self) -> int:
        return self['login']

    def name(self) -> str:
        return self['name']

    def server(self) -> str:
        return self['server']

    def company(self) -> str:
        return self['company']

    def mode(self) -> str:
        return self['mode']

    def leverage(self) -> int:
        return self['leverage']

    def order_limit(self) -> int:
        return self['orderLimit']

    def currency(self) -> str:
        return self['currency']

    def balance(self) -> float:
        return self['balance']

    def credit(self) -> float:
        return self['credit']

    def profit(self) -> float:
        return self['profit']

    def equity(self) -> float:
        return self['equity']

    def margin(self) -> float:
        return self['margin']

    def free_margin(self) -> float:
        return self['freeMargin']

    def margin_level(self) -> float:
        return self['marginLvl']

    def is_trade_allowed(self) -> bool:
        return self['canTrade']

    def is_expert_allowed(self) -> bool:
        return self['canExpert']
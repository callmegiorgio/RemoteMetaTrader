from rmt import jsonutil, Tick, Account
from ..  import Content

class GetAccountResponse:
    def __init__(self, content: Content):
        self._account = Account(
            login          = jsonutil.read_required(content, 'login',      int),
            name           = jsonutil.read_required(content, 'name',       str),
            server         = jsonutil.read_required(content, 'server',     str),
            company        = jsonutil.read_required(content, 'company',    str),
            mode           = jsonutil.read_required(content, 'mode',       str),
            leverage       = jsonutil.read_required(content, 'leverage',   int),
            order_limit    = jsonutil.read_required(content, 'orderLimit', int),
            currency       = jsonutil.read_required(content, 'currency',   str),
            balance        = jsonutil.read_required(content, 'balance',    float),
            credit         = jsonutil.read_required(content, 'credit',     float),
            profit         = jsonutil.read_required(content, 'profit',     float),
            equity         = jsonutil.read_required(content, 'equity',     float),
            margin         = jsonutil.read_required(content, 'margin',     float),
            free_margin    = jsonutil.read_required(content, 'freeMargin', float),
            margin_level   = jsonutil.read_required(content, 'marginLvl',  float),
            trade_allowed  = jsonutil.read_required(content, 'canTrade',   bool),
            expert_allowed = jsonutil.read_required(content, 'canExpert',  bool),
        )
    
    def account(self) -> Account:
        return self._account
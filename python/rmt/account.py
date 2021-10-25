from enum import Enum
from .    import SlottedClass

class TradeMode(Enum):
    DEMO    = 'demo'
    REAL    = 'real'
    CONTEST = 'contest'

class MarginMode(Enum):
    PERCENT = 'percent'
    MONEY   = 'money'

class Account(SlottedClass):
    """Stores information about a trading account."""

    __slots__ = [
        '_login',
        '_name',
        '_server',
        '_company',
        '_trade_mode',
        '_margin_mode',
        '_leverage',
        '_order_limit',
        '_currency',
        '_balance',
        '_credit',
        '_profit',
        '_equity',
        '_margin',
        '_free_margin',
        '_margin_level',
        '_margin_call_level',
        '_margin_stop_level',
        '_trade_allowed',
        '_expert_allowed'
    ]

    def __init__(self,
                 login: int,
                 name: str,
                 server: str,
                 company: str,
                 trade_mode: TradeMode,
                 margin_mode: MarginMode,
                 leverage: int,
                 order_limit: int,
                 currency: str,
                 balance: float,
                 credit: float,
                 profit: float,
                 equity: float,
                 margin: float,
                 free_margin: float,
                 margin_level: float,
                 margin_call_level: float,
                 margin_stop_out_level: float,
                 trade_allowed: bool,
                 expert_allowed: bool
    ):
        self._login             = int(login)
        self._name              = str(name)
        self._server            = str(server)
        self._company           = str(company)
        self._trade_mode        = TradeMode(trade_mode)
        self._margin_mode       = MarginMode(margin_mode)
        self._leverage          = int(leverage)
        self._order_limit       = int(order_limit)
        self._currency          = str(currency)
        self._balance           = float(balance)
        self._credit            = float(credit)
        self._profit            = float(profit)
        self._equity            = float(equity)
        self._margin            = float(margin)
        self._free_margin       = float(free_margin)
        self._margin_level      = float(margin_level)
        self._margin_call_level = float(margin_call_level)
        self._margin_stop_level = float(margin_stop_out_level)
        self._trade_allowed     = bool(trade_allowed)
        self._expert_allowed    = bool(expert_allowed)

    @property
    def login(self) -> int:
        return self._login

    @property
    def name(self) -> str:
        return self._name

    @property
    def server(self) -> str:
        return self._server

    @property
    def company(self) -> str:
        return self._company

    @property
    def trade_mode(self) -> TradeMode:
        return self._trade_mode

    @property
    def margin_mode(self) -> MarginMode:
        return self._margin_mode

    @property
    def leverage(self) -> int:
        return self._leverage

    @property
    def order_limit(self) -> int:
        return self._order_limit

    @property
    def currency(self) -> str:
        return self._currency

    @property
    def balance(self) -> float:
        return self._balance

    @property
    def credit(self) -> float:
        return self._credit

    @property
    def profit(self) -> float:
        return self._profit

    @property
    def equity(self) -> float:
        return self._equity

    @property
    def margin(self) -> float:
        return self._margin

    @property
    def free_margin(self) -> float:
        return self._free_margin

    @property
    def margin_level(self) -> float:
        return self._margin_level

    @property
    def margin_call_level(self) -> float:
        return self._margin_call_level

    @property
    def margin_stop_out_level(self) -> float:
        return self._margin_stop_level

    @property
    def is_trade_allowed(self) -> bool:
        return self._trade_allowed

    @property
    def is_expert_allowed(self) -> bool:
        return self._expert_allowed
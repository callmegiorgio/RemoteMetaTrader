from rmt import jsonutil
from ..  import Content

class GetInstrumentResponse:
    def __init__(self, content: Content):
        self._description         = jsonutil.read_optional(content, 'desc',       str)
        self._base_currency       = jsonutil.read_optional(content, 'bcurrency',  str)
        self._profit_currency     = jsonutil.read_optional(content, 'pcurrency',  str)
        self._margin_currency     = jsonutil.read_optional(content, 'mcurrency',  str)
        self._decimal_places      = jsonutil.read_required(content, 'ndecimals',  int)
        self._point               = jsonutil.read_required(content, 'point',      float)
        self._tick_size           = jsonutil.read_required(content, 'ticksz',     float)
        self._contract_size       = jsonutil.read_required(content, 'contractsz', float)
        self._lot_step            = jsonutil.read_required(content, 'lotstep',    float)
        self._min_lot             = jsonutil.read_required(content, 'minlot',     float)
        self._max_lot             = jsonutil.read_required(content, 'maxlot',     float)
        self._min_stop_lvl        = jsonutil.read_required(content, 'minstop',    int)
        self._freeze_lvl          = jsonutil.read_required(content, 'freezelvl',  int)
        self._spread              = jsonutil.read_required(content, 'spread',     int)

    def description(self) -> str:
        return self._description

    def base_currency(self) -> str:
        return self._base_currency

    def profit_currency(self) -> str:
        return self._profit_currency

    def margin_currency(self) -> str:
        return self._margin_currency

    def decimal_places(self) -> int:
        return self._decimal_places

    def point(self) -> float:
        return self._point

    def tick_size(self) -> float:
        return self._tick_size

    def contract_size(self) -> float:
        return self._contract_size

    def lot_step(self) -> float:
        return self._lot_step

    def min_lot(self) -> float:
        return self._min_lot

    def max_lot(self) -> float:
        return self._max_lot

    def min_stop_level(self) -> int:
        return self._min_stop_lvl

    def freeze_level(self) -> int:
        return self._freeze_lvl

    def spread(self) -> int:
        return self._spread
from . import Response

class GetInstrument(Response):
    content_layout = {
        'desc':       str,
        'bcurrency':  str,
        'pcurrency':  str,
        'mcurrency':  str,
        'ndecimals':  int,
        'point':      float,
        'ticksz':     float,
        'contractsz': float,
        'lotstep':    float,
        'minlot':     float,
        'maxlot':     float,
        'minstop':    int,
        'freezelvl':  int,
        'spread':     int
    }

    def description(self) -> str:
        return self['desc']

    def base_currency(self) -> str:
        return self['bcurrency']

    def profit_currency(self) -> str:
        return self['pcurrency']

    def margin_currency(self) -> str:
        return self['mcurrency']

    def decimal_places(self) -> int:
        return self['ndecimals']

    def point(self) -> float:
        return self['point']

    def tick_size(self) -> float:
        return self['ticksz']

    def contract_size(self) -> float:
        return self['contractsz']

    def lot_step(self) -> float:
        return self['lotstep']

    def min_lot(self) -> float:
        return self['minlot']

    def max_lot(self) -> float:
        return self['maxlot']

    def min_stop_level(self) -> int:
        return self['minstop']

    def freeze_level(self) -> int:
        return self['freezelvl']

    def spread(self) -> int:
        return self['spread']
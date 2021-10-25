from . import Response

class GetInstrument(Response):
    content_layout = {
        'desc':         (str, ''),
        'bcurrency':    (str, ''),
        'qcurrency':    (str, ''),
        'mcurrency':    (str, ''),
        'ndecimals':    int,
        'point':        float,
        'tickSize':     float,
        'contractSize': float,
        'lotStep':      float,
        'minLot':       float,
        'maxLot':       float,
        'minStop':      int,
        'freezeLvl':    int,
        'spread':       int
    }

    def description(self) -> str:
        return self['desc']

    def base_currency(self) -> str:
        return self['bcurrency']

    def quote_currency(self) -> str:
        return self['qcurrency']

    def margin_currency(self) -> str:
        return self['mcurrency']

    def decimal_places(self) -> int:
        return self['ndecimals']

    def point(self) -> float:
        return self['point']

    def tick_size(self) -> float:
        return self['tickSize']

    def contract_size(self) -> float:
        return self['contractSize']

    def lot_step(self) -> float:
        return self['lotStep']

    def min_lot(self) -> float:
        return self['minLot']

    def max_lot(self) -> float:
        return self['maxLot']

    def min_stop_level(self) -> int:
        return self['minStop']

    def freeze_level(self) -> int:
        return self['freezeLvl']

    def spread(self) -> int:
        return self['spread']
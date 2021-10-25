from . import Response

class GetInstruments(Response):
    content_layout = [
        {
            'symbol':       str,
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
    ]

    def instrument_count(self) -> int:
        return len(self)

    def symbol(self, index: int) -> str:
        return self[index]['symbol']

    def description(self, index: int) -> str:
        return self[index]['desc']

    def base_currency(self, index: int) -> str:
        return self[index]['bcurrency']

    def quote_currency(self, index: int) -> str:
        return self[index]['qcurrency']

    def margin_currency(self, index: int) -> str:
        return self[index]['mcurrency']

    def decimal_places(self, index: int) -> int:
        return self[index]['ndecimals']

    def point(self, index: int) -> float:
        return self[index]['point']

    def tick_size(self, index: int) -> float:
        return self[index]['tickSize']

    def contract_size(self, index: int) -> float:
        return self[index]['contractSize']

    def lot_step(self, index: int) -> float:
        return self[index]['lotStep']

    def min_lot(self, index: int) -> float:
        return self[index]['minLot']

    def max_lot(self, index: int) -> float:
        return self[index]['maxLot']

    def min_stop_level(self, index: int) -> int:
        return self[index]['minStop']

    def freeze_level(self, index: int) -> int:
        return self[index]['freezeLvl']

    def spread(self, index: int) -> int:
        return self[index]['spread']
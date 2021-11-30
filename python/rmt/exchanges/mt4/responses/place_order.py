from . import Response

class PlaceOrder(Response):
    content_layout = {
        'ticket':     int,
        'lots':       float,
        'op':         float,
        'ot':         str,
        'commission': float,
        'profit':     float,
        'swap':       float
    }

    def ticket(self) -> int:
        return self['ticket']

    def lots(self) -> float:
        return self['lots']

    def open_price(self) -> float:
        return self['op']

    def open_time(self) -> str:
        return self['ot']

    def commission(self) -> float:
        return self['commission']

    def profit(self) -> float:
        return self['profit']

    def swap(self) -> float:
        return self['swap']
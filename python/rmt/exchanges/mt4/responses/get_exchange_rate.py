from . import Response

class GetExchangeRate(Response):
    content_layout = {
        'rate': float
    }

    def rate(self) -> float:
        return self['rate']
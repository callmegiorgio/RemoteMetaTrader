from . import Response

class GetTick(Response):
    content_layout = {
        'time': str,
        'bid':  float,
        'ask':  float
    }

    def time(self) -> str: 
        return self['time']

    def bid(self) -> float: 
        return self['bid']

    def ask(self) -> float: 
        return self['ask']
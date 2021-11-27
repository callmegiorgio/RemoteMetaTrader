from . import Response

class GetTick(Response):
    content_layout = {
        'time': int,
        'bid':  float,
        'ask':  float
    }

    def server_time(self) -> int: 
        return self['time']

    def bid(self) -> float: 
        return self['bid']

    def ask(self) -> float: 
        return self['ask']
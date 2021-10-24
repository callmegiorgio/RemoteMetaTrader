from datetime import datetime, timezone
from .        import Response

class GetTick(Response):
    content_layout = {
        'time': int,
        'bid':  float,
        'ask':  float
    }

    def server_time(self) -> int: 
        return datetime.fromtimestamp(self['time'], timezone.utc)

    def bid(self) -> float: 
        return self['bid']

    def ask(self) -> float: 
        return self['ask']
from datetime import datetime, timezone
from rmt      import jsonutil, Tick
from ..       import Content

class GetTickResponse:
    def __init__(self, content: Content):
        server_time = jsonutil.read_required(content, 'time', int)
        bid         = jsonutil.read_required(content, 'bid',  float)
        ask         = jsonutil.read_required(content, 'ask',  float)

        self._tick = Tick(
            server_time = datetime.fromtimestamp(server_time, timezone.utc),
            bid = bid,
            ask = ask
        )
    
    def tick(self) -> Tick:
        return self._tick
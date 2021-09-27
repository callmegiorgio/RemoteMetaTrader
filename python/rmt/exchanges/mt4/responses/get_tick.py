from datetime   import datetime, timezone
from typing     import Dict
from rmt        import jsonutil, Tick
from ..requests import GetTickRequest
from .          import Response

class GetTickResponse(Response):
    command = GetTickRequest.command

    def deserialize(self, obj: Dict):
        server_time = jsonutil.read_required(obj, 'server_time', int)
        bid         = jsonutil.read_required(obj, 'bid',         float)
        ask         = jsonutil.read_required(obj, 'ask',         float)

        self._tick = Tick(
            server_time = datetime.fromtimestamp(server_time, timezone.utc),
            bid = bid,
            ask = ask
        )
    
    def tick(self) -> Tick:
        return self._tick
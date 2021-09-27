from typing     import Dict, List
from rmt        import jsonutil
from ..requests import WatchSymbolRequest
from .          import Response

class WatchSymbolResponse(Response):
    command = WatchSymbolRequest.command

    def deserialize(self, obj: Dict):
        self._symbols: List[str] = jsonutil.read_optional_key(obj, 'symbols', List)

    def symbols(self) -> List[str]:
        return self._symbols
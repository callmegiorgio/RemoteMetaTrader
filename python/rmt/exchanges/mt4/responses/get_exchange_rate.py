from rmt import jsonutil
from ..  import Content

class GetExchangeRateResponse:
    def __init__(self, content: Content):
        self._rate = jsonutil.read_required(content, 'rate', float)
    
    def rate(self) -> float:
        return self._rate
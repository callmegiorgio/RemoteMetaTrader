from datetime   import datetime, timezone
from typing     import Dict, List
from rmt        import Bar, jsonutil
from ..requests import GetBarsRequest
from .          import Response

class GetBarsResponse(Response):
    command = GetBarsRequest.command

    def deserialize(self, obj: Dict):
        root_arr = jsonutil.read_required_key(obj, 'bars', List)
        
        self._bars: List[Bar] = []

        for i, _ in enumerate(root_arr):
            sub_arr = jsonutil.read_required_index(root_arr, i, List)
            t       = jsonutil.read_required_index(sub_arr,  0, int)
            o       = jsonutil.read_required_index(sub_arr,  1, float)
            h       = jsonutil.read_required_index(sub_arr,  2, float)
            l       = jsonutil.read_required_index(sub_arr,  3, float)
            c       = jsonutil.read_required_index(sub_arr,  4, float)

            bar = Bar(
                    time  = datetime.fromtimestamp(t, timezone.utc),
                    open  = o,
                    high  = h,
                    low   = l,
                    close = c
                )

            self._bars.append(bar)

    def bars(self) -> List[Bar]:
        return self._bars
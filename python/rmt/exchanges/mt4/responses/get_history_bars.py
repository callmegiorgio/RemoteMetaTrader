from datetime import datetime, timezone
from typing   import List
from rmt      import Bar, jsonutil
from ..       import Content

class GetHistoryBarsResponse:
    def __init__(self, content: Content):
        self._bars: List[Bar] = []

        for i, _ in enumerate(content):
            bar = jsonutil.read_required(content, i, list)
            t   = jsonutil.read_required(bar,     0, int)
            o   = jsonutil.read_required(bar,     1, float)
            h   = jsonutil.read_required(bar,     2, float)
            l   = jsonutil.read_required(bar,     3, float)
            c   = jsonutil.read_required(bar,     4, float)

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
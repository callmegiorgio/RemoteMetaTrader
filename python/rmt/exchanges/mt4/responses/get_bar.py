from datetime import datetime, timezone
from rmt      import Bar, jsonutil
from ..       import Content

class GetBarResponse:
    def __init__(self, content: Content):
        t = jsonutil.read_required(content, 0, int)
        o = jsonutil.read_required(content, 1, float)
        h = jsonutil.read_required(content, 2, float)
        l = jsonutil.read_required(content, 3, float)
        c = jsonutil.read_required(content, 4, float)
        v = jsonutil.read_required(content, 5, int)

        self._bar = Bar(
            time   = datetime.fromtimestamp(t, timezone.utc),
            open   = o,
            high   = h,
            low    = l,
            close  = c,
            volume = v
        )

    def bar(self) -> Bar:
        return self._bar
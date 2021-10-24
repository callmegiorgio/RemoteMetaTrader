from datetime import datetime, timezone
from .        import Response

class GetHistoryBars(Response):
    content_layout = [[int, float, float, float, float]]

    def bar_count(self) -> int:
        return len(self)

    def time(self, index: int) -> datetime:
        return datetime.fromtimestamp(self[index][0], timezone.utc)

    def open(self, index: int) -> float:
        return self[index][1]

    def high(self, index: int) -> float:
        return self[index][2]

    def low(self, index: int) -> float:
        return self[index][3]

    def close(self, index: int) -> float:
        return self[index][4]
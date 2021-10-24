from datetime import datetime, timezone
from .        import Response

class GetBar(Response):
    content_layout = [int, float, float, float, float, int]

    def time(self) -> datetime:
        return datetime.fromtimestamp(self[0], timezone.utc)

    def open(self) -> float:
        return self[1]

    def high(self) -> float:
        return self[2]

    def low(self) -> float:
        return self[3]

    def close(self) -> float:
        return self[4]

    def volume(self) -> int:
        return self[5]
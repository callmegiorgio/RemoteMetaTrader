from datetime import datetime, timezone
from .        import Event

class TickEvent(Event):
    content_layout = [int, float, float]

    def symbol(self) -> str:
        return self.dynamic_name

    def server_time(self) -> datetime:
        return datetime.fromtimestamp(self[0], timezone.utc)

    def bid(self) -> float:
        return self[1]

    def ask(self) -> float:
        return self[2]
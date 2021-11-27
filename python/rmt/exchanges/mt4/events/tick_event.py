from . import Event

class TickEvent(Event):
    content_layout = [int, float, float]

    def symbol(self) -> str:
        return self.dynamic_name

    def server_time(self) -> int:
        return self[0]

    def bid(self) -> float:
        return self[1]

    def ask(self) -> float:
        return self[2]
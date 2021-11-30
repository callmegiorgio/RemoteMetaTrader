from . import Event

class TickEvent(Event):
    content_layout = [str, float, float]

    def symbol(self) -> str:
        return self.dynamic_name

    def time(self) -> str:
        return self[0]

    def bid(self) -> float:
        return self[1]

    def ask(self) -> float:
        return self[2]
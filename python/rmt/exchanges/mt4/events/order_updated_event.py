from . import Event

class OrderUpdatedEvent(Event):
    content_layout = {
        'ticket':     int,
        'comment':    (str, ''),
        'commission': float,
        'profit':     float,
        'swap':       float
    }

    def ticket(self) -> int:
        return self['ticket']

    def comment(self) -> str:
        return self['comment']

    def commission(self) -> float:
        return self['commission']

    def profit(self) -> float:
        return self['profit']

    def swap(self) -> float:
        return self['swap']
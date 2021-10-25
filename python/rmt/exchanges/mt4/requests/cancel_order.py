from .. import Content
from .  import Request

class CancelOrder(Request):
    command = 'cancelOrder'

    def __init__(self, ticket: int):
        super().__init__()

        self._ticket = ticket

    def content(self) -> Content:
        msg = {
            'ticket': self._ticket
        }

        return msg
from .. import Content
from .  import Request

class CancelOrderRequest(Request):
    command = 'cancelOrder'

    def __init__(self, ticket: int):
        super().__init__()

        self._ticket = ticket

    def content(self) -> Content:
        msg = {
            'ticket': self._ticket
        }

        return msg
from .. import Content
from .  import Request

class GetAccount(Request):
    command = 'getAccount'

    def content(self) -> Content:
        return {}
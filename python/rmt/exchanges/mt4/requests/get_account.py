from .. import Content
from .  import Request

class GetAccountRequest(Request):
    command = 'getAccount'

    def content(self) -> Content:
        return {}
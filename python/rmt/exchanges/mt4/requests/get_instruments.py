from .. import Content
from .  import Request

class GetInstrumentsRequest(Request):
    command = 'getInstruments'

    def __init__(self):
        super().__init__()

    def content(self) -> Content:
        return {}
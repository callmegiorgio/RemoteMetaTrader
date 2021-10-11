from rmt import error
from ..  import Content

class Event:
    """Represents an event that ocurred on the exchange server."""

    def __init__(self, dynamic_name: str, content: Content):
        raise error.NotImplementedException(self.__class__, '__init__')
from rmt import JsonModel
from ..  import Content

class Event(JsonModel):
    """Represents an event that ocurred on the exchange server."""

    content_layout = {}

    def __init__(self, dynamic_name: str, content: Content):
        super().__init__(self.content_layout, content)

        self._dynamic_name = dynamic_name

    @property
    def dynamic_name(self) -> str:
        return self._dynamic_name
from typing import Dict, List, Union
from rmt    import JsonModel

class Response(JsonModel):
    content_layout = {}

    def __init__(self, content: Union[Dict, List]):
        super().__init__(self.content_layout, content)
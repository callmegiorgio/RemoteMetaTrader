from typing     import Dict
from ..requests import ModifyOrderRequest
from .          import Response

class ModifyOrderResponse(Response):
    command = ModifyOrderRequest.command

    def deserialize(self, obj: Dict):
        pass

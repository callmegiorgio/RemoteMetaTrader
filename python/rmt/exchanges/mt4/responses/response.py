import json
from typing import Dict
from rmt    import jsonutil
#pprint

class Response:
    command = ''

    def __init__(self, response: str):
        obj = json.loads(response)

        if not isinstance(obj, Dict):
            raise TypeError('response object is not of type JSON object')

        result = jsonutil.read_required(obj, 'result', int)
        param = obj.get('param', '')

        if result != 0:
            raise ValueError('result != 0: %s' % result)
        
        self.deserialize(obj)

        # result = error.ErrorCode(result)

        # if result == error.ErrorCode.NO_ERROR or result == error.ErrorCode.NO_MQLERROR:
        #     self.deserialize(obj)
        # elif result == error.ErrorCode.USER_UNKNOWN_COMMAND:
        #     raise error.UnknownServerCommand(self.command())
        # elif result == error.ErrorCode.USER_MISSING_REQUIRED_PARAM:
        #     raise error.MissingRequiredParameter(self.command(), param)
        # elif result == error.ErrorCode.USER_INVALID_PARAMETER_TYPE:
        #     raise error.InvalidParameterType(self.command(), param)
        # elif result == error.ErrorCode.USER_INVALID_PARAMETER_VALUE:
        #     raise error.InvalidParameterValue(self.command(), param)
        # else: # any(result == ec.value for ec in error.ErrorCode):
        #     raise error.ExecutionError(self.command(), result)

    def deserialize(self, obj: Dict):
        raise NotImplementedError(self.deserialize.__name__)
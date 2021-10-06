from typing import Any, Type

class RMTError(Exception):
    pass

class NotImplementedException(RMTError):
    def __init__(self, class_type: Type[Any], method_name: str):
        error_msg = 'method {} of class {} is not implemented'.format(method_name, class_type)

        super().__init__(error_msg)

class RequestError(RMTError):
    pass

class RequestTimeout(RequestError):
    pass

class ExecutionError(RMTError):
    pass
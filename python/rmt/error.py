class RMTError(Exception):
    pass

class RequestError(RMTError):
    pass

class RequestTimeout(RequestError):
    pass

class ExecutionError(RMTError):
    pass
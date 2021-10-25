from typing    import Callable, Dict, NoReturn, Optional
from rmt       import JsonModel
from rmt.error import RequestError, ExecutionError, InvalidOrderStatus
from .         import CommandResultCode, Content

class MQL4Error(ExecutionError):
    """Raised if an MQL4 error occurs."""

    def __init__(self, command: str, code: CommandResultCode):
        error_msg = (
            "execution of command '{0}' failed with code {1} ({2})" 
            .format(command, code.value, code.name)
        )

        super().__init__(error_msg)

        self._code = code

    @property
    def code(self) -> Optional[int]:
        return self._code

def _raise_invalid_request(command: str, content: Dict) -> NoReturn:
    raise RequestError("Invalid request (command was '{}')".format(command))

def _raise_unknown_request_command(command: str, content: Dict) -> NoReturn:
    raise RequestError("Server does not recognize command '{}'".format(command))

def _raise_invalid_json(command: str, content: Dict) -> NoReturn:
    raise RequestError("Request content at command '{}' is not valid JSON".format(command))

def _raise_missing_json_key(command: str, content: Dict) -> NoReturn:
    model = JsonModel({'key': (str, '?')}, content)
    
    key = model['key']

    raise RequestError("Missing JSON key '{0}' at command '{1}'".format(key, command))

def _raise_missing_json_index(command: str, content: Dict) -> NoReturn:
    model = JsonModel({'index': (int, '?')})

    index = model['index']

    raise RequestError("Missing JSON index {0} at command '{1}'".format(index, command))

def _raise_invalid_json_key_type(command: str, content: Dict) -> NoReturn:
    model = JsonModel(
        {
            'key':      (str, '?'),
            'actual':   (str, '?'),
            'expected': (str, '?')
        },
        content
    )

    key           = model['key']
    actual_type   = model['actual']
    expected_type = model['expected']

    raise RequestError(
        "JSON key '{0}' at command '{1}' has invalid type (expected: {2}, got: {3})"
        .format(key, command, expected_type, actual_type)
    )

def _raise_invalid_json_index_type(command: str, content: Dict) -> NoReturn:
    model = JsonModel(
        {
            'index':    (int, '?'),
            'actual':   (str, '?'),
            'expected': (str, '?')
        },
        content
    )

    index         = model['index']
    actual_type   = model['actual']
    expected_type = model['expected']

    raise RequestError(
        "JSON index {0} at command '{1}' has invalid type (expected: {2}, got: {3})"
        .format(index, command, expected_type, actual_type)
    )

def _raise_invalid_order_status(command: str, content: Dict) -> NoReturn:
    model = JsonModel({'actual': (str, '')}, content)

    actual_status = model['actual']
    #TODO: expected_status

    raise InvalidOrderStatus(actual_status)

RaiseFunction = Callable[[str, Dict], NoReturn]

_raise_function_table: Dict[CommandResultCode, RaiseFunction] = {
    CommandResultCode.INVALID_REQUEST:         _raise_invalid_request,
    CommandResultCode.UNKNOWN_REQUEST_COMMAND: _raise_unknown_request_command,
    CommandResultCode.INVALID_JSON:            _raise_invalid_json,
    CommandResultCode.MISSING_JSON_KEY:        _raise_missing_json_key,
    CommandResultCode.MISSING_JSON_INDEX:      _raise_missing_json_index,
    CommandResultCode.INVALID_JSON_KEY_TYPE:   _raise_invalid_json_key_type,
    CommandResultCode.INVALID_JSON_INDEX_TYPE: _raise_invalid_json_index_type,
    CommandResultCode.INVALID_ORDER_STATUS:    _raise_invalid_order_status
}

def raise_error(command: str, result_code: CommandResultCode, content: Content) -> NoReturn:
    is_valid_result_code = any(v == result_code for v in CommandResultCode)  

    if not is_valid_result_code:
        raise RequestError("request failed by unknown error {}".format(result_code))

    if result_code in _raise_function_table:
        raise_function = _raise_function_table[result_code]
        raise_function(command, content)
    else:
        raise MQL4Error(command, result_code)
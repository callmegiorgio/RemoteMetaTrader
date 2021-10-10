from typing    import Callable, Dict, NoReturn, Optional
from rmt       import jsonutil, OrderStatus
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
    raise RequestError("Invalid request (command was '%s')" % command)

def _raise_unknown_request_command(command: str, content: Dict) -> NoReturn:
    raise RequestError("Server does not recognize command '%s'" % command)

def _raise_invalid_json(command: str, content: Dict) -> NoReturn:
    raise RequestError("Request content at command '%s' is not valid JSON" % command)

def _raise_missing_json_key(command: str, content: Dict) -> NoReturn:
    key = jsonutil.read_optional(content, 'key', str, '?')

    raise RequestError("Missing JSON key '%s' at command '%s'" % (key, command))

def _raise_missing_json_index(command: str, content: Dict) -> NoReturn:
    index = jsonutil.read_optional(content, 'index', int, '?')

    raise RequestError("Missing JSON index %s at command '%s'" % (index, command))

def _raise_invalid_json_key_type(command: str, content: Dict) -> NoReturn:
    key           = jsonutil.read_optional(content, 'key',      str, '?')
    actual_type   = jsonutil.read_optional(content, 'actual',   str, '?')
    expected_type = jsonutil.read_optional(content, 'expected', str, '?')

    raise RequestError(
        "JSON key '%s' at command '%s' has invalid type (expected: %s, got: %s)"
        % (key, command, expected_type, actual_type)
    )

def _raise_invalid_json_index_type(command: str, content: Dict) -> NoReturn:
    index         = jsonutil.read_optional(content, 'index',    int, '?')
    actual_type   = jsonutil.read_optional(content, 'actual',   str, '?')
    expected_type = jsonutil.read_optional(content, 'expected', str, '?')

    raise RequestError(
        "JSON index %s at command '%s' has invalid type (expected: %s, got: %s)"
        % (index, command, expected_type, actual_type)
    )

def _raise_invalid_order_status(command: str, content: Dict) -> NoReturn:
    actual_status   = jsonutil.read_optional(content, 'actual', str)
    #expected_status = jsonutil.read_optional(content, 'expected', str, '?')

    valid_statuses = [s.name.lower().replace('_', ' ') for s in OrderStatus]

    if actual_status not in valid_statuses:
        actual_status = '?'

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
        raise RequestError("request failed by unknown error %s" % result_code)

    if result_code in _raise_function_table:
        raise_function = _raise_function_table[result_code]
        raise_function(command, content)
    else:
        raise MQL4Error(command, result_code)
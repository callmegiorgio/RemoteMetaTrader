from typing import Callable, Dict, NoReturn
from rmt    import error, jsonutil
from .      import CommandResultCode, Content

def _raise_invalid_request(command: str, content: Dict) -> NoReturn:
    raise error.RequestError("Invalid request (command was '%s')" % command)

def _raise_unknown_request_command(command: str, content: Dict) -> NoReturn:
    raise error.RequestError("Server does not recognize command '%s'" % command)

def _raise_invalid_json(command: str, content: Dict) -> NoReturn:
    raise error.RequestError("Request content at command '%s' is not valid JSON" % command)

def _raise_missing_json_key(command: str, content: Dict) -> NoReturn:
    key = jsonutil.read_optional(content, 'key', str, '?')

    raise error.RequestError("Missing JSON key '%s' at command '%s'" % (key, command))

def _raise_missing_json_index(command: str, content: Dict) -> NoReturn:
    index = jsonutil.read_optional(content, 'index', int, '?')

    raise error.RequestError("Missing JSON index %s at command '%s'" % (index, command))

def _raise_invalid_json_key_type(command: str, content: Dict) -> NoReturn:
    key           = jsonutil.read_optional(content, 'key',      str, '?')
    actual_type   = jsonutil.read_optional(content, 'actual',   str, '?')
    expected_type = jsonutil.read_optional(content, 'expected', str, '?')

    raise error.RequestError(
        "JSON key '%s' at command '%s' has invalid type (expected: %s, got: %s)"
        % (key, command, expected_type, actual_type)
    )

def _raise_invalid_json_index_type(command: str, content: Dict) -> NoReturn:
    index         = jsonutil.read_optional(content, 'index',    int, '?')
    actual_type   = jsonutil.read_optional(content, 'actual',   str, '?')
    expected_type = jsonutil.read_optional(content, 'expected', str, '?')

    raise error.RequestError(
        "JSON index %s at command '%s' has invalid type (expected: %s, got: %s)"
        (index, command, expected_type, actual_type)
    )

def _raise_invalid_order_status(command: str, content: Dict) -> NoReturn:
    actual_status   = jsonutil.read_optional(content, 'actual',   str, '?')
    expected_status = jsonutil.read_optional(content, 'expected', str, '?')

    raise error.RequestError(
        "Cannot execute command '%s' with the order's status (expected: %s, got %s)"
        % (command, expected_status, actual_status)
    )

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
        raise error.RequestError("request failed by unknown error %s" % result_code)

    if result_code in _raise_function_table:
        raise_function = _raise_function_table[result_code]
        raise_function(command, content)
    else:
        raise error.ExecutionError(
            "execution of command '%s' failed with code %s (%s)"
            % (command, result_code.value, result_code.name)
        )
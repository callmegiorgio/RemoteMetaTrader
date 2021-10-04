from datetime import datetime, timezone
from typing   import Any, Dict, List, Type, Union

def _ensure_type_or_raise(pos: Union[str, int], value: Any, ExpectedType: Type[Any]):
    if not isinstance(value, ExpectedType):
        if isinstance(pos, str):
            raise TypeError(
                "value at key '%s' is of invalid JSON type (expected: %s, got: %s)" 
                % (pos, type(value), type(ExpectedType))
            )
        else:
            raise TypeError(
                "value at index %s is of invalid JSON type (expected: %s, got: %s)"
                % (pos, type(value), type(ExpectedType))
            )

def _ensure_type_or_default(value: Any, ExpectedType: Type[Any], *default: Any):
    if isinstance(value, ExpectedType):
        return value
    
    if len(default) > 0:
        return default[0]
    else:
        return ExpectedType()

def read_required(container: Union[Dict, List], pos: Union[str, int], ExpectedType: Type[Any]):
    value = container[pos]

    if ExpectedType == datetime:
        _ensure_type_or_raise(pos, value, int)
        return datetime.fromtimestamp(value, timezone.utc)
    else:
        _ensure_type_or_raise(pos, value, ExpectedType)
        return value

def read_optional(container: Union[Dict, List], pos: Union[str, int], ExpectedType: Type[Any], *default: Any):
    value = None

    try:
        value = container[pos]
    except (KeyError, IndexError):
        pass

    if ExpectedType == datetime:
        value = _ensure_type_or_default(value, int, *default)

        if isinstance(value, int):
            return datetime.fromtimestamp(value, timezone.utc)
        else:
            return value
    else:
        return _ensure_type_or_default(value, ExpectedType, *default)
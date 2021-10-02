from typing import Any, Dict, List, Type, Union

def read_required(container: Union[Dict, List], pos: Union[str, int], ExpectedType: Type[Any]):
    value = container[pos]

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

    return value

def read_optional(container: Union[Dict, List], pos: Union[str, int], ExpectedType: Type[Any], *default: Any):
    value = None

    try:
        value = container[pos]
    except (KeyError, IndexError):
        pass

    if isinstance(value, ExpectedType):
        return value

    if len(default) > 0:
        return default[0]
    
    return ExpectedType()
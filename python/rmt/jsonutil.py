from typing import Dict, List, Union
from rmt import error

def read_required_key(obj: Dict, key: str, expected_type):
    if key not in obj:
        raise error.InvalidResponse("missing key '{}'".format(key))
    
    value = obj[key]

    if value is None:
        return expected_type()

    if not isinstance(value, expected_type):
        raise error.InvalidResponse("value for key '{}' is of type {} (expected: {})".format(key, type(value), expected_type))

    return value

def read_required_index(arr: List, index: int, expected_type):
    value = arr[index]

    if value is None:
        return expected_type()

    if not isinstance(value, expected_type):
        raise error.InvalidResponse("value at index '{}' is of type {} (expected: {})".format(index, type(value), expected_type))
    
    return value

def read_required(parent: Union[Dict, List], pos: Union[str, int], expected_type):
    if isinstance(parent, Dict):
        if isinstance(pos, str):
            return read_required_key(parent, pos, expected_type)
        else:
            raise ValueError("expected 'str' for argument 'pos' of read_required() whose 'parent' is type Dict (got: '{}')".format(type(pos)))
    elif isinstance(parent, List):
        if isinstance(pos, int):
            return read_required_index(parent, pos, expected_type)
        else:
            raise ValueError("expected 'int' for argument 'pos' of read_required() whose 'parent' is type List (got: '{}')".format(type(pos)))
    else:
        raise ValueError("expected argument 'parent' of read_required() to be of type Dict or List (got: '{}')".format(type(parent)))

def read_optional(obj: dict, key: str, expected_type):
    value = obj.get(key, expected_type())

    if not isinstance(value, expected_type):
        return expected_type()
    
    return value
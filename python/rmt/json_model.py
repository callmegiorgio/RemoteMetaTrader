from typing import Any, Dict, List, Tuple, Union
from rmt    import SlottedClass

class JsonModel(SlottedClass):
    """Reads a JSON document according to predefined type model.

    Description
    -----------
    The class `JsonModel` performs type-checking of a JSON document according to
    a type model. The model may be a `dict` or a `list` object, which represent
    a JSON object or JSON array, respectively.

    The model object is similar to a JSON document, but contains types instead of
    instances. Tuples are used to indicate optionality, and must contain a default
    value as the last element:

    >>> expected_model = {
    ...     'a': int,
    ...     'b': bool,
    ...     'c': str,
    ...     'd': (str, None),
    ...     'e': {
    ...         'f': float,
    ...         'g': [int] # zero or more int
    ...     },
    ...     'h': [(int, str, 'element is neither int nor str')], # zero or more int|str
    ...     'i': [int, float], # exactly two elements: one int followed by one float
    ...     'j': [(int, bool, 'neither int nor bool'), (str, float, 'neither str nor float')]
    ... }
    >>> actual_json = {
    ...     'a': 1,
    ...     'b': True,
    ...     'c': 'hello',
    ...     'd': 1,
    ...     'e': {
    ...        'f': 10.2,
    ...        'g': [1, 2, 3, 4, 5]
    ...     },
    ...     'h': [1024, 3.14, True, 'yo'],
    ...     'i': [123, 456.789],
    ...     'j': ['hello', False]
    ... }
    >>> model = JsonModel(expected_model, actual_json)
    >>> model['a']
    1
    >>> model['b']
    True
    >>> model['c']
    'hello'
    >>> str(model['d'])
    'None'
    >>> model['e']['f']
    10.2
    >>> model['e']['g'][2]
    3
    >>> model['h'][0]
    1024
    >>> model['h'][1]
    'element is neither int nor str'
    >>> model['h'][2]
    'element is neither int nor str'
    >>> model['h'][3]
    'yo'
    >>> model['i'][0]
    123
    >>> model['i'][1]
    456.789
    >>> model['j'][0]
    'neither int nor bool'
    >>> model['j'][1]
    'neither str nor float'
    """

    __slots__ = ['_expected_json', '_actual_json']

    def __init__(self, expected_json: Union[Dict, List], actual_json: Union[Dict, List]):
        
        if not isinstance(expected_json, (dict, list)):
            raise ValueError(
                "expected JSON document in JsonModel must be of type 'dict' or 'list' (got: {})"
                .format(type(expected_json))
            )

        if type(actual_json) != type(expected_json):
            raise ValueError(
                'type mismatching between expected JSON and actual JSON documents in JsonModel (expected: {}, got: {})'
                .format(type(expected_json), type(actual_json))
            )

        self._expected_json = expected_json
        self._actual_json   = actual_json.copy()
        
        if isinstance(expected_json, dict):
            self._read_dict()
        else:
            self._read_list()

    def __getitem__(self, pos: Union[str, int]):
        return self._actual_json[pos]

    def _read_dict(self):
        for key, expected_type_or_value in self._expected_json.items():
            try:
                key   = str(key)
                value = self._actual_json[key]

                if type(expected_type_or_value) == type:
                    if expected_type_or_value in (dict, list, tuple):
                        raise ValueError('expected type must not be dict, list, or tuple')

                    if isinstance(value, expected_type_or_value):
                        continue
                else:
                    if isinstance(expected_type_or_value, (dict, list)):
                        self._actual_json[key] = JsonModel(expected_type_or_value, value)
                        continue
                
                    if isinstance(expected_type_or_value, tuple):
                        self._actual_json[key] = self._read_tuple_item(value, expected_type_or_value)
                        continue
            
                raise TypeError(
                    "invalid type of value at key '{0}' in JsonModel object (expected type: {1}, got: {2})"
                    .format(key, expected_type_or_value, type(value))
                )

            except KeyError:
                if isinstance(expected_type_or_value, tuple):
                    self._actual_json[key] = self._read_tuple_item(value, expected_type_or_value)
                else:
                    raise KeyError(
                        "missing required key '{}' in actual JSON document of JsonModel"
                        .format(key)
                    ) from None

    def _read_list(self):
        expected_json_len = len(self._expected_json)
        
        if expected_json_len == 0:
            raise ValueError('expected array in JsonModel is 0-sized (expected size: > 0)')
        
        for index, value in enumerate(self._actual_json):
            expected_type_or_value = None

            if expected_json_len == 1:
                expected_type_or_value = self._expected_json[0]
            else:
                try:
                    expected_type_or_value = self._expected_json[index]
                except IndexError:
                    raise IndexError(
                        "expected array index {0} out of bounds in JsonModel (array size: {1})"
                        .format(index, expected_json_len)
                    ) from None

            if type(expected_type_or_value) == type:
                if expected_type_or_value in (dict, list, tuple):
                    raise ValueError('expected type must not be dict, list, or tuple')

                if isinstance(value, expected_type_or_value):
                    continue
            else:
                if isinstance(expected_type_or_value, (dict, list)):
                    self._actual_json[index] = JsonModel(expected_type_or_value, value)
                    continue
            
                if isinstance(expected_type_or_value, tuple):
                    self._actual_json[index] = self._read_tuple_item(value, expected_type_or_value)
                    continue

            raise TypeError(
                'invalid type of value at index {0} in JsonModel array (expected type: {1}, got: {2})'
                .format(index, expected_type_or_value, type(value))
            )

    def _read_tuple_item(self, value: Any, types: Tuple) -> Any:
        types_len = len(types)

        if types_len < 2:
            raise ValueError(
                'expected JSON document in JsonModel has invalid-sized tuple (expected size: >= 2, got: {})'
                .format(types_len)
            )

        default_value = types[-1]
        types         = types[:(types_len - 1)]

        for t in types:
            if type(value) == t:
                return value

        return default_value

    def __str__(self) -> str:
        return str(self._actual_json)
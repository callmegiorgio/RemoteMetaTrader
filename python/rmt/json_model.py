from __future__ import annotations
from typing     import Any, Dict, List, Optional, Tuple, Type, Union
from rmt        import SlottedClass

class JsonModelPosition(SlottedClass):
    __slots__ = ['_pos', '_parent']

    def __init__(self, pos: Union[str, int], parent: Optional[JsonModelPosition] = None):
        self._pos    = pos
        self._parent = parent

    def path(self) -> str:
        path    = ''
        current = self

        while True:
            if current._parent is None:
                path = str(current._pos) + path
                break

            if type(current._pos) == str:
                path = '.' + current._pos + path
            else:
                path = '[' + str(current._pos) + ']' + path

            current = current._parent

        return path

    def __str__(self) -> str:
        if type(self._pos) == str:
            return "key '{}'".format(self.path())
        else:
            return "index {}".format(self.path())

class JsonModelError(Exception):
    """Raised if JSON model provided to `JsonModel` is invalid."""
    pass

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

    >>> expected_json = {
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
    >>> model = JsonModel(expected_json, actual_json)
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

    __slots__ = ['_expected_json', '_actual_json', '_parent_pos']

    def __init__(self,
                 expected_json: Union[Dict, List],
                 actual_json: Union[Dict, List, None] = None,
                 _parent_pos: Optional[JsonModelPosition] = None
    ):
        if not isinstance(expected_json, (dict, list)):
            raise JsonModelError(
                "expected JSON document in JsonModel must be of type 'dict' or 'list' (got: {})"
                .format(type(expected_json))
            )

        self._expected_json = expected_json
        self._parent_pos    = _parent_pos
        
        if actual_json is not None:
            self.read(actual_json)

    def read(self, actual_json: Union[Dict, List]):
        if type(actual_json) != type(self._expected_json):
            raise TypeError(
                'type mismatching between expected JSON and actual JSON documents in JsonModel (expected: {0}, got: {1})'
                .format(type(self._expected_json), type(actual_json))
            )

        self._actual_json = actual_json.copy()
        
        if isinstance(self._expected_json, dict):
            self._read_dict()
        else:
            self._read_list()

    def __len__(self) -> int:
        return len(self._actual_json)

    def __getitem__(self, pos: Union[str, int]):
        return self._actual_json[pos]

    def _read_dict(self):
        if len(self._expected_json) == 0:
            raise JsonModelError('expected JSON is an empty object (expected object with at least one element)')

        for key, model_element in self._expected_json.items():
            key = str(key)
            actual_value = None
            pos = JsonModelPosition(key, self._parent_pos)

            try:
                actual_value = self._actual_json[key]
            except KeyError:
                if isinstance(model_element, tuple):
                    self._actual_json[key] = self._read_value_with_tuple_element(
                        pos,
                        model_element,
                        None
                    )
                else:
                    raise KeyError(
                        "missing required {} in actual JSON document of JsonModel"
                        .format(pos)
                    ) from None

            self._actual_json[key] = self._read_value(pos, model_element, actual_value)

    def _read_list(self):
        expected_json_len = len(self._expected_json)
        
        if expected_json_len == 0:
            raise JsonModelError('JsonModel has invalid 0-sized array (expected size: > 0)')
        
        if expected_json_len == 1:
            self._read_variable_size_list()
        else:
            self._read_fixed_size_list()

    def _read_fixed_size_list(self):
        expected_json_len = len(self._expected_json)
        actual_json_len   = len(self._actual_json)

        for index, model_element in enumerate(self._expected_json):
            actual_value = None
            pos          = JsonModelPosition(index, self._parent_pos)

            try:
                actual_value = self._actual_json[index]
            except IndexError:
                raise IndexError(
                    "failed to read value at {0} (expected array size: {1}; actual size: {2})"
                    .format(pos, expected_json_len, actual_json_len)
                ) from None

            self._actual_json[index] = self._read_value(pos, model_element, actual_value)

        if actual_json_len > expected_json_len:
            self._actual_json = self._actual_json[:expected_json_len]

    def _read_variable_size_list(self):
        model_element = self._expected_json[0]

        for index, actual_value in enumerate(self._actual_json):
            pos = JsonModelPosition(index, self._parent_pos)

            self._actual_json[index] = self._read_value(pos, model_element, actual_value)

    def _read_value(self, pos: JsonModelPosition, model_element: Any, actual_value: Any) -> Any:
        if type(model_element) == type:
            return self._read_value_with_type_element(pos, model_element, actual_value)
        else:
            return self._read_value_with_instance_element(pos, model_element, actual_value)
    
    def _read_value_with_type_element(self, pos: JsonModelPosition, model_element: Type[Any], actual_value: Any) -> Any:
        if model_element not in (str, int, float, bool, None):
            raise JsonModelError(
                "at {0}: invalid model type (expected: str, int, float, bool, or None; got: {1})"
                .format(pos, model_element)
            )

        if type(actual_value) != model_element:
            raise TypeError(
                'invalid value type at {0} of JsonModel (expected type: {1}, got: {2})'
                .format(pos, model_element, type(actual_value))
            )
        
        return actual_value

    def _read_value_with_instance_element(self, pos: JsonModelPosition, model_element: Any, actual_value: Any):
        if model_element is None:
            if actual_value is not None:
                raise TypeError(
                    'invalid value type at {0} of JsonModel (expected type: NoneType; got: {1})'
                    .format(pos, type(actual_value))
                )

            return actual_value

        if type(model_element) == tuple:
            return self._read_value_with_tuple_element(pos, model_element, actual_value)

        if type(model_element) not in (dict, list):
            raise JsonModelError(
                'invalid instance of model element (expected: dict, list, tuple, or NoneType; got: {})'
                .format(type(model_element))
            )

        if type(actual_value) != type(model_element):
            expected_model_element_type = list if type(model_element) == list else dict

            raise TypeError(
                'invalid value type at {0} of JsonModel (expected type: {1}; got: {2})'
                .format(pos, expected_model_element_type, type(actual_value))
            )
        
        return JsonModel(model_element, actual_value, pos)

    def _read_value_with_tuple_element(self, pos: JsonModelPosition, tuple_element: Tuple, actual_value: Any) -> Any:
        tuple_len = len(tuple_element)

        if tuple_len < 2:
            raise JsonModelError(
                'JsonModel has invalid-sized tuple at {0} (expected size: >= 2, got: {1})'
                .format(pos, tuple_len)
            )

        default_value = tuple_element[-1]
        tuple_element = tuple_element[:(tuple_len - 1)]

        for index, elem in enumerate(tuple_element):
            try:
                return self._read_value(JsonModelPosition(index, pos), elem, actual_value)
            except TypeError:
                pass

        return default_value

    def __str__(self) -> str:
        return str(self._actual_json)

    def __repr__(self) -> str:
        return str(self)
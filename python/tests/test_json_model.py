from unittest import TestCase
from rmt      import JsonModel, JsonModelError

class TestJsonModel(TestCase):
    def test_raises_on_invalid_document(self):
        expected_json = 'neither dict nor list'
        actual_json   = ...
        
        self.assertRaises(JsonModelError, JsonModel, expected_json, actual_json)

    def test_raises_on_empty_dict(self):
        self.assertRaises(JsonModelError, JsonModel, {}, {})

    def test_raises_on_empty_list(self):
        self.assertRaises(JsonModelError, JsonModel, [], [])

    def test_raises_on_missing_key(self):
        self.assertRaises(KeyError, JsonModel, {'a': int}, {})
        self.assertRaises(KeyError, JsonModel, {'a': int}, {'b': 1})
        self.assertRaises(KeyError, JsonModel, {'a': int}, {'c': 2, 'd': 3})

    def test_raises_on_missing_index_in_fixed_size_list(self):
        self.assertRaises(IndexError, JsonModel, [int, float],       [1])
        self.assertRaises(IndexError, JsonModel, [int, float, bool], [1, 2.34])

    def test_raises_on_invalid_dict_element_type(self):
        self.assertRaises(TypeError, JsonModel, {'a': int}, {'a': 1.23})
        self.assertRaises(TypeError, JsonModel, {'a': int}, {'a': True})
        self.assertRaises(TypeError, JsonModel, {'a': int}, {'a': False})
        self.assertRaises(TypeError, JsonModel, {'a': int}, {'a': 'not int'})

    def test_raises_on_invalid_list_element_type(self):
        self.assertRaises(TypeError, JsonModel, [int], [1.23])
        self.assertRaises(TypeError, JsonModel, [int], [True])
        self.assertRaises(TypeError, JsonModel, [int], [False])
        self.assertRaises(TypeError, JsonModel, [int], ['not int'])

    def test_reads_dict(self):
        model = JsonModel({'a': int}, {'a': 123})

        self.assertEquals(model['a'], 123)
        self.assertEquals(len(model), 1)

    def test_reads_fixed_size_list(self):
        model = JsonModel([bool, int, bool, str], [True, 24, False, '74 Is the New 24'])

        self.assertEquals(model[0], True)
        self.assertEquals(model[1], 24)
        self.assertEquals(model[2], False)
        self.assertEquals(model[3], '74 Is the New 24')

    def test_reads_empty_variable_size_list(self):
        model = JsonModel([str], [])

        self.assertEquals(len(model), 0)        

    def test_reads_nonempty_variable_size_list(self):
        model = JsonModel([str], ['a', 'b', 'c'])

        self.assertEquals(model[0], 'a')
        self.assertEquals(model[1], 'b')
        self.assertEquals(model[2], 'c')

    def test_reads_optional_value_in_dict(self):
        model = JsonModel({'k': (int, 'not an int')})

        model.read({'k': 123})
        self.assertEquals(model['k'], 123)

        model.read({'k': 456.789})
        self.assertEquals(model['k'], 'not an int')

    def test_reads_optional_dict(self):
        model = JsonModel([({'a': int}, 'not a dict')])

        model.read([1])
        self.assertEquals(model[0], 'not a dict')

        model.read([{'a': 1}])
        self.assertEquals(model[0]['a'], 1)

    def test_reads_optional_value_in_fixed_size_list(self):
        model = JsonModel([(int, bool, 'neither int nor bool'), (str, float, 'neither str nor float')])

        model.read([1, 'a'])
        self.assertEquals(model[0], 1)
        self.assertEquals(model[1], 'a')

        model.read(['a', 'b'])
        self.assertEquals(model[0], 'neither int nor bool')
        self.assertEquals(model[1], 'b')

        model.read([True, None])
        self.assertEquals(model[0], True)
        self.assertEquals(model[1], 'neither str nor float')

    def test_ignores_exceeding_elements_on_fixed_size_list(self):
        model = JsonModel([None, bool, int], [None, True, 2, 34.56, '789'])

        self.assertEquals(model[0], None)
        self.assertEquals(model[1], True)
        self.assertEquals(model[2], 2)
        self.assertEquals(len(model), 3)
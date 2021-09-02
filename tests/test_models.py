import unittest

from cli3.models import Folder, InputField


class MyTestCase(unittest.TestCase):
    def test_folder(self):
        json_folder = {
            'name': 'test'
        }
        folder = Folder(json_folder)
        self.assertEqual(folder.name, json_folder['name'])

    def test_input_dield(self):
        json_field = dict(type='test_type',
                          nci='test-nci',
                          nci_column='test_column',
                          values='values')
        field = InputField(json_field)
        self.assertEqual(field.type, json_field['type'])
        self.assertEqual(field.nci, json_field['nci'])
        self.assertEqual(field.nci_column, json_field['nci_column'])
        self.assertEqual(field.values, json_field['values'])


if __name__ == '__main__':
    unittest.main()

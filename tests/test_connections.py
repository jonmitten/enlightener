"""Test enlightener."""

import sys
import unittest
sys.path.append('../enlightener')

from enlightener import get_device_list, hello, connect_to_api, hello_sheets


class TestConnector(unittest.TestCase):
    """Test connections."""

    def test_hello(self):
        """Test import."""
        self.assertEqual(hello(), 'hello world')

    def test_connect_to_api(self):
        """Test API connectivity."""
        # make sure a 200 is returned.
        response = connect_to_api(True)
        self.assertEqual(
            response.status_code, 200)

    def test_get_device_list(self):
        nose_test = False
        resp = get_device_list()
        mylist = resp['devices']
        test_device_list = ['99000512002128', '99000512000619']
        for device in test_device_list:
            if device in mylist:
                nose_test = True
        self.assertEqual(nose_test, True)

    def test_hello_sheets(self):
        values = hello_sheets()

        self.assertIn(['99000512002128', '1'], values)

if __name__ == '__main__':
    unittest.main()

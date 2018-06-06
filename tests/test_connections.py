"""Test connection module."""
import unittest
import sys
sys.path.append('../enlightener')

from connections import connect_to_api
from google_sheets import hello_sheets, input_from_sheets, write_to_cell


class TestConnector(unittest.TestCase):
    """Test connections."""

    def test_hello_sheets(self):
        """Test connectivity to Google Sheets API."""
        values = hello_sheets()

        self.assertIn(['99000512000619', '50'], values)

    def test_connect_to_api(self):
        """Test API connectivity."""
        # make sure a 200 is returned.
        response = connect_to_api(True)
        self.assertEqual(
            response.status_code, 200)

    def test_write_to_cell(self):
        write_to_cell("Hello, from test_connections!", "Sheet1", "E17")
        test_ = input_from_sheets("Sheet1!E17")
        self.assertEqual(test_, [["Hello, from test_connections!"]])

if __name__ == '__main__':
    unittest.main()

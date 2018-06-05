"""Test connection module."""


import unittest
import sys
sys.path.append('../enlightener')

from enlightener import connect_to_api
from google_sheets import hello_sheets


class TestConnector(unittest.TestCase):
    """Test connections."""

    def test_hello_sheets(self):
        """Test connectivity to Google Sheets API."""
        values = hello_sheets()

        self.assertIn(['99000512002128', '1'], values)

    def test_connect_to_api(self):
        """Test API connectivity."""
        # make sure a 200 is returned.
        response = connect_to_api(True)
        self.assertEqual(
            response.status_code, 200)


if __name__ == '__main__':
    unittest.main()

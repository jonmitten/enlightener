"""Test enlightener."""

import sys
sys.path.append('../enlightener')


import unittest

from enlightener import *


class TestConnections(unittest.TestCase):
    """Test connections."""

    def test_hello(self):
        """Test import."""
        self.assertEqual(Enlightener.hello(self), 'hello world')

    def test_connect_to_api(self):
        """Test API connectivity."""
        # make sure a 200 is returned.
        self.assertEqual(Enlightener.connect_to_api(devicelist, True).status_code, 200)

if __name__ == '__main__':
    unittest.main()

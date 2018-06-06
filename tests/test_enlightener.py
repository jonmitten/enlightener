"""Test Enlightener module."""

import unittest
import sys
sys.path.append('../enlightener')

from enlightener import analyze_time_diff
from enlightener import compile_light_time
from enlightener import get_device_list, get_light_threshold, get_time_diff
from enlightener import get_device_ids, process_device_ids, update_device_light_thresholds


class TestConnector(unittest.TestCase):
    """Test connections."""

    def setUp(self):
        """Set up."""
        self.device1 = '99000512002151'
        self.sheet_values = [
            ['99000512002128', '1'],
            ['99000512000619', '2']
        ]
        self.new_values = [
            ['99000512000621', '256'],
            ['99000512000648', '512']
        ]

        self.test_device_list = ['99000512002128', '99000512000619']

        self.time1 = '2018-06-01 00:00:00'
        self.time2 = '2018-06-01 00:05:00'
        self.time3 = '2018-06-01 00:10:00'
        self.time4 = '2018-06-01 00:15:00'
        self.time5 = '2018-06-01 00:20:00'

    def test_get_light_threshold(self):
        """Test light threshold fetch."""
        comp = compile_light_time(self.device1)
        threshold = comp['light']

        self.assertGreater(
            int(threshold), 0)

    def test_get_device_list(self):
        """Test device list fetch."""
        bool_test = False
        resp = get_device_list()
        mylist = resp['devices']
        test_device_list = self.test_device_list

        for device in test_device_list:
            if device in mylist:
                bool_test = True
        self.assertEqual(bool_test, True)

    def test_analyze_time_diff(self):
        """Test time diff processor."""
        diff1 = get_time_diff(self.time1, self.time2)
        diff2 = get_time_diff(self.time1, self.time3)
        diff3 = get_time_diff(self.time1, self.time4)
        diff4 = get_time_diff(self.time1, self.time5)

        self.assertLessEqual(diff1, 5)
        self.assertLessEqual(diff2, 10)
        self.assertLessEqual(diff3, 15)
        self.assertGreaterEqual(diff3, 15)
        self.assertGreaterEqual(diff4, 20)

    def test_get_device_ids(self):
        values = get_device_ids()
        self.assertIn('99000512000619', values)

    # def test_process_device_ids(self):
    #     """Test the process runner."""
    #     process = process_device_ids()
    #     print('\n')
    #     print(process)
    #     print('\n')
    #     reprocess = process_device_ids()
    #     print('\n')
    #     print(reprocess)
    #     print('\n')

    def test_update_device_light_thresholds(self):
        data = update_device_light_thresholds(True)


if __name__ == '__main__':
    unittest.main()

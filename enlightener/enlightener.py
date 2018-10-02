"""
Main module for Enlightener app.

Run this as follows:
"""
import datetime
import logging
import math
import time

from connections import (get_config_for_device,
                         get_status_for_device,
                         locate_now,
                         update_light_value)
from google_sheets import (input_from_sheets,
                           light_threshold_status_cell,
                           time_checked_cell,
                           report_status_cell,
                           update_sheet_status,
                           time_since_last_report_cell)
from settings import SHEET, RANGE_NAME, ROW_ITER_START
from utilities import (get_timestamp,
                       get_current_light_reading,
                       get_light_threshold,
                       get_time_diff,
                       analyze_time_diff,
                       now)

logger = logging.getLogger('ENLIGHTENER')


def analyze_thresholds(values):
    """
    Take in values, parse rows, compare desired thresholds.

    act accordingly.
    """
    if values['desired'] == values['current']:
        return True
    return False


def compile_light_time(device_id):
    """Process time and light."""
    config = get_config_for_device(device_id)
    status = get_status_for_device(device_id)

    _now = now()
    timestamp = get_timestamp(status)
    light = get_light_threshold(config)
    time_diff = round(get_time_diff(timestamp, _now))
    analysis = analyze_time_diff(time_diff, device_id)
    light_reading = get_current_light_reading(status)

    # print("time: {}, light:{}, 'time_diff': {}, 'analysis': {}".format(
    #     timestamp,
    #     light,
    #     time_diff,
    #     analysis)
    # )

    return({
        'now': _now,
        'time': timestamp,
        'light': light,
        'time difference': time_diff,
        'analysis': analysis,
        'light_reading': light_reading
    })


def get_device_ids():
    """Get each device from the designated spreadsheet."""
    values = input_from_sheets("{}!A2:B2".format(SHEET))
    print("get_device_ids() values: {}".format(values))
    device_ids = []
    for x in values:
        device_id = x[0]
        locate_now(device_id)
        device_ids.append(device_id)
    return device_ids


def get_pretty_time(minutes):
    """Return a pretty time."""
    sec = datetime.timedelta(seconds=int(minutes * 60))
    d = datetime.datetime(1, 1, 1) + sec

    return ("%d:%d:%d" % (d.day - 1, d.hour, d.minute))


def update_device_light_thresholds(test=False):
    """
    Get PT unit ID.

    Desired Light Sensor Value,
    and current light sensor value.
    """
    data = input_from_sheets(RANGE_NAME)
    i = ROW_ITER_START
    light_threshold_status = {}
    now_status = {}
    report_status = {}
    diff_status = {}
    current_light_reading = {}

    for row in data:
        device_id = row[0]

        """Process a location stamp."""
        time.sleep(math.floor(100 / 24))
        # set up the write range for updating sheet
        light_time = compile_light_time(device_id)
        # fetch the current light sensor value and timestamp

        desired_threshold_value = row[1]

        light_threshold_status['value'] = light_time.get('light')
        light_threshold_status['cell'] = "C{}".format(str(i))

        now_status['value'] = light_time.get('now')
        now_status['cell'] = "D{}".format(str(i))

        report_status['value'] = light_time.get('time')
        report_status['cell'] = "F{}".format(str(i))

        diff_minutes = light_time.get('time difference')
        pretty_time = get_pretty_time(diff_minutes)

        diff_status['value'] = "{}".format(pretty_time)
        diff_status['cell'] = "G{}".format(str(i))

        current_light_reading['value'] = light_time.get('light_reading')
        current_light_reading['cell'] = "H{}".format(str(i))

        update_sheet_status(
            light_threshold_status=light_threshold_status,
            now_status=now_status,
            report_status=report_status,
            diff_status=diff_status,
            current_light_reading=current_light_reading,
        )
        time.sleep(math.floor(100 / 24))
        # compare current light value with desired light value
        # desired_threshold = input_from_sheets("B{}".format(str(i)), '')

        analysis = analyze_thresholds(
            {'desired': int(desired_threshold_value),
             'current': int(light_threshold_status['value'])})

        # get a timestamp
        now = datetime.datetime.utcnow()
        attempt_or_verify_time = now.strftime("%Y-%m-%d %H:%M:%S")
        cell = 'E{}'.format(str(i))
        print("DIFF MINUTES\n\n\n\n\n\n\n\n{}".format(diff_minutes))
        # if different, update to desired light value
        if diff_minutes > 32:
            update_sheet_status(
                check_battery={'value': 'CHECK BATTERY', 'cell': cell})
        else:
            print('''\n\n\n\n\n
                ANALYSIS for {device}
                with light threshold of {threshold}
                where {desired} is desired: {analysis}
                \n\n\n\n\n\n\n'''.format(
                device=device_id,
                analysis=analysis,
                threshold=light_threshold_status['value'],
                desired=desired_threshold_value))
            time.sleep(1)
            if not analysis:
                update_light_value(device_id, desired_threshold_value)
                update_sheet_status(
                    light_update={'value': 'attempted {}'.format(
                        attempt_or_verify_time), 'cell': cell})
            else:
                update_sheet_status(light_update={
                    'value': 'verified {}'.format(attempt_or_verify_time),
                    'cell': cell})
        # finally, update the increment var
        print('''\n\n\n\n\n\n\n\n\n\n\n
            let's take a breather...
            \n\n\n\n\n\n\n\n\n\n\n
            ''')
        time.sleep(math.floor(100 / 24))
        print("back to work!")
        i += 1

    return {'data': data, 'time': report_status['value']}


def report_light_threshold_values(init_data=""):
    """Grab light reading and report it.

    Light Threshold:       | C col
    .......................|.......
    Time Checked:          | D col
    .......................|.......
    Time Checked:          | E col
    .......................|.......
    Last Unit Report Time: | F col
    .......................|.......
    Time Since Last Report:| G col
    """
    light_threshold_status = {}
    now_status = {}
    report_status = {}
    diff_status = {}
    data = {}
    if init_data is "":
        data = input_from_sheets(RANGE_NAME)
    else:
        data = init_data
    i = ROW_ITER_START
    for row in data:
        device_id = row[0]
        time_diff = 0
        config = get_config_for_device(device_id)
        status = get_status_for_device(device_id)
        _now = now()
        timestamp = get_timestamp(status)
        light_threshold = get_light_threshold(config)
        light_threshold_status['value'] = light_threshold
        # light_threshold_status['cell'] = "C{}".format(str(i))
        light_threshold_status['cell'] = light_threshold_status_cell(i)

        now_status['value'] = _now
        now_status['cell'] = time_checked_cell(i)

        report_status['value'] = timestamp
        report_status['cell'] = report_status_cell(i)

        time_diff = round(get_time_diff(timestamp, _now))
        pretty_time = get_pretty_time(time_diff)

        diff_status['value'] = "{}".format(pretty_time)
        diff_status['cell'] = time_since_last_report_cell(i)

        update_sheet_status(
            light_threshold_status=light_threshold_status,
            now_status=now_status,
            report_status=report_status,
            diff_status=diff_status
        )
        time.sleep(math.floor(100 / 24))
        i += 1


def report_light_readings():
    """Grab light reading and report it.

    Time Checked:          | D col
    .......................|.......
    Last Unit Report Time: | F col
    .......................|.......
    Light Reading:         | H col
    """
    # Get all data
    data = input_from_sheets(RANGE_NAME)
    now_status = report_status = current_light_reading = {}
    i = ROW_ITER_START
    for row in data:

        device_id = row[0]

        light_time = compile_light_time(device_id)
        now_status['value'] = light_time.get('now')
        now_status['cell'] = "D{}".format(str(i))

        report_status['value'] = light_time.get('time')
        report_status['cell'] = "F{}".format(str(i))

        current_light_reading['value'] = light_time.get('light_reading')
        current_light_reading['cell'] = "H{}".format(str(i))

        update_sheet_status(
            now_status=now_status,
            report_status=report_status,
            current_light_reading=current_light_reading,
        )
        i += 1
    print("finished running report_light_readings")


def read_write(switch="read"):
    """Switch between read thresholds or write new thresholds."""
    if switch is "read":
        report_light_threshold_values()
    elif switch is "write":
        update_device_light_thresholds()


if __name__ == '__main__':
    read_write("read")
    pass

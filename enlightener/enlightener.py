"""
Main module for Enlightener app.

Run this as follows:
"""
import datetime
import logging
import math
import time
import types

from connections import (get_config_for_device,
                         get_status_for_device,
                         locate_now,
                         update_light_value,
                         get_production_pt_units)
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
    if config and status:
        _now = now()
        timestamp = get_timestamp(status)
        light = get_light_threshold(config)
        time_diff = round(get_time_diff(timestamp, _now))
        analysis = analyze_time_diff(time_diff, device_id)
        light_reading = get_current_light_reading(status)
    else:
        _now = now()
        timestamp = 'I got a 401 or some other error'
        light = 'I got a 401 or some other error'
        time_diff = 'I got a 401 or some other error'
        analysis = 'I got a 401 or some other error'
        light_reading = 'I got a 401 or some other error'

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
    try:
        d = datetime.datetime(1, 1, 1) + sec
        return ("%d:%d:%d" % (d.day - 1, d.hour, d.minute))
    except:
        d = "Error"
        return ("{} from get pretty time".format(d))


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
    i = ROW_ITER_START
    light_threshold_status = {}
    now_status = {}
    report_status = {}
    diff_status = {}
    data = {}

    if init_data is "":
        data = input_from_sheets(RANGE_NAME)
    else:
        data = init_data

    for row in data:
        device_id = row[0]
        time_diff = 0
        config = get_config_for_device(device_id)
        status = get_status_for_device(device_id)
        if config and status:
            print("got config and status")
            s = update_unit_status(status, config, time_diff, i)
        else:
            print("didn't get config and status")
            s = update_unit_status_failure(i)
        light_threshold_status = s.light_threshold_status
        now_status = s.now_status
        report_status = s.report_status
        diff_status = s.diff_status
        update_sheet_status(
            light_threshold_status=light_threshold_status,
            now_status=now_status,
            report_status=report_status,
            diff_status=diff_status
        )
        time.sleep(math.floor(100 / 24))
        i += 1
    print("Finished running report of threshold values.")


def update_unit_status_failure(iterator):
    """Fill in values with error message to push to spreadsheet."""
    s = types.SimpleNamespace()
    s.light_threshold_status = {}
    s.now_status = {}
    s.report_status = {}
    s.diff_status = {}
    alert = "I got a 401"
    s.light_threshold_status['value'] = alert
    s.light_threshold_status['cell'] = light_threshold_status_cell(iterator)
    s.now_status['value'] = alert
    s.now_status['cell'] = time_checked_cell(iterator)
    s.report_status['value'] = alert
    s.report_status['cell'] = report_status_cell(iterator)
    s.diff_status['value'] = alert
    s.diff_status['cell'] = time_since_last_report_cell(iterator)
    return s


def update_unit_status(status, config, time_diff, iterator):
    """Combine values with cell positions in a dictionary."""
    s = types.SimpleNamespace()
    s.light_threshold_status = {}
    s.now_status = {}
    s.report_status = {}
    s.diff_status = {}
    s._now = now()
    s.timestamp = get_timestamp(status)
    s.light_threshold = get_light_threshold(config)
    s.light_threshold_status['value'] = s.light_threshold
    # light_threshold_status['cell'] = "C{}".format(str(i))
    s.light_threshold_status['cell'] = light_threshold_status_cell(iterator)

    s.now_status['value'] = s._now
    s.now_status['cell'] = time_checked_cell(iterator)

    s.report_status['value'] = s.timestamp
    s.report_status['cell'] = report_status_cell(iterator)

    try:
        s.time_diff = round(get_time_diff(s.timestamp, s._now))
    except TypeError:
        s.time_diff = -1

    if s.time_diff > 32:
        check_battery = True
    else:
        check_battery = False
    s.check_battery = check_battery
    s.pretty_time = "CHECK BATTERY" if check_battery else get_pretty_time(
        s.time_diff)

    s.diff_status['value'] = "{}".format(s.pretty_time)
    s.diff_status['cell'] = time_since_last_report_cell(iterator)

    return s


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
        now = light_time.get('now')
        status_time = light_time.get('time')
        light_reading = light_time.get('light_reading')

        light_reading_or_batt = get_light_value_or_no_battery(
            status_time, now, light_reading)

        now_status['value'] = now
        now_status['cell'] = "D{}".format(str(i))

        report_status['value'] = status_time
        report_status['cell'] = "F{}".format(str(i))

        current_light_reading['value'] = light_reading_or_batt
        current_light_reading['cell'] = "H{}".format(str(i))

        update_sheet_status(
            now_status=now_status,
            report_status=report_status,
            current_light_reading=current_light_reading,
        )
        i += 1
        time.sleep(math.floor(100 / 24))
    print("finished running report_light_readings")


def get_light_value_or_no_battery(time, now, value):
    """For light threshold readings, put value or check battery."""
    time_diff = round(get_time_diff(time, now))
    if time_diff > 32:
        return "CHECK BATTERY"
    return value


def evois_threshold_check():
    """Enlightened evoIS threshold check."""
    production_units = get_production_pt_units()
    i = ROW_ITER_START
    pt_unit = {}
    owner = {}
    activated = {}
    evo_type = {}
    sheet_name = 'evois_device_threshold_check'
    for row in production_units:
        print("row: {}".format(row))
        # time.sleep(5)
        # unique columns to Production checks:
        pt_unit['value'] = row['unit_id']
        pt_unit['cell'] = "A{}".format(str(i))
        print(pt_unit)
        # time.sleep(5)
        owner['value'] = row['owner']
        owner['cell'] = "I{}".format(str(i))
        print(owner)
        # time.sleep(5)
        activated['value'] = row['activated']
        activated['cell'] = "J{}".format(str(i))
        print(activated)
        # time.sleep(5)
        evo_type['value'] = row['evo_type']
        evo_type['cell'] = "K{}".format(str(i))
        print(evo_type)
        # time.sleep(5)
        # and their respective cells:
        print("owner: {}, activated: {}, evo_type: {}, pt_unit: {}".format(
            owner, activated, evo_type, pt_unit))
        update_sheet_status(
            pt_unit=pt_unit,
            owner=owner,
            activated=activated,
            evo_type=evo_type,
            sheet=sheet_name,
        )
        i += 1


def read_write(switch="read"):
    """Switch between read thresholds or write new thresholds."""
    if switch is "read":
        get_device_ids()
        report_light_threshold_values()
        report_light_readings()
    elif switch is "thresholds":
        get_device_ids()
        report_light_threshold_values()
    elif switch is "write":
        get_device_ids()
        update_device_light_thresholds()
        update_device_light_thresholds()
    elif switch is "light":
        get_device_ids()
        report_light_readings()
    elif switch is "all":
        get_device_ids()
        report_light_threshold_values()
        report_light_readings()
        update_device_light_thresholds()
        update_device_light_thresholds()
    elif switch is "evois":
        print('Checking evoIS thresholds')
        evois_threshold_check()
        report_light_threshold_values()
    else:
        print("You didn't select a valid switch...")

if __name__ == '__main__':
    read_write("read")  # change this line to perform read_write tasks
    pass

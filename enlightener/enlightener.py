"""
Main module for Enlightener app.

Run this as follows:
"""
import datetime
import logging
import math
import time

from collections import deque
from connections import (get_config_for_device,
                         get_device_list,
                         get_status_for_device,
                         update_light_value)
from google_sheets import (input_from_sheets,
                           write_to_cell)

logger = logging.getLogger('ENLIGHTENER')



def analyze_thresholds(values):
    """
    Take in values, parse rows, compare desired thresholds,
    act accordingly.
    """
    if values['desired'] == values['current']:
        return True
    return False


def get_timestamp(req):
    """Get timestamp from req."""
    timestamp = req.get('statusTimeStamp')

    return timestamp


def chop_microseconds(delta):
    """Make deltas without microseconds."""
    return delta - datetime.timedelta(microseconds=delta.microseconds)


def get_time_diff(timestamp, now):
    """Get time delta between two times."""
    now = datetime.datetime.strptime(str(now), '%Y-%m-%d %H:%M:%S')
    status_time = datetime.datetime.strptime(
        timestamp, '%Y-%m-%d %H:%M:%S')
    minute = datetime.timedelta(seconds=60)
    time_diff = (now - status_time) / minute

    return round(time_diff)


def analyze_time_diff(diff, device_id):
    """Analyze and return assessement of diff."""
    if diff is 0:
        return "{} last reported {}".format(device_id, 'moments ago')
    return "{} last reported {} minutes ago".format(device_id, diff)


def get_light_threshold(req):
    """Get light from req."""
    light_threshold = req.get("highlight")

    return light_threshold


def compile_light_time(device_id):
    """Process time and light."""
    now = datetime.datetime.utcnow()
    now = now.replace(microsecond=0)
    config = get_config_for_device(device_id)
    status = get_status_for_device(device_id)

    timestamp = get_timestamp(status)
    light = get_light_threshold(config)
    time_diff = round(get_time_diff(timestamp, now))
    analysis = analyze_time_diff(time_diff, device_id)

    # print("time: {}, light:{}, 'time_diff': {}, 'analysis': {}".format(
    #     timestamp,
    #     light,
    #     time_diff,
    #     analysis)
    # )

    return({
        'now': str(now),
        'time': timestamp,
        'light': light,
        'time difference': time_diff,
        'analysis': analysis
    })


def get_device_ids():
    """Get each device from the designated spreadsheet."""
    values = input_from_sheets("Sheet1!A1:B2")
    device_ids = []
    del values[0]
    for x in values:
        device_id = x[0]
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
    sheet = 'Sheet1!'
    data = input_from_sheets("{}A2:B100".format(sheet))
    i = 2
    light_status = {}
    now_status = {}
    report_status = {}
    diff_status = {}
    for row in data:
        device_id = row[0]
        # set up the write range for updating sheet
        light_time = compile_light_time(device_id)
        # fetch the current light sensor value and timestamp
        light_status['value'] = light_time.get('light')
        light_status['cell'] = "C{}".format(str(i))

        now_status['value'] = light_time.get('now')
        now_status['cell'] = "D{}".format(str(i))

        report_status['value'] = light_time.get('time')
        report_status['cell'] = "F{}".format(str(i))

        diff_minutes = light_time.get('time difference')
        pretty_time = get_pretty_time(diff_minutes)

        diff_status['value'] = "{}".format(pretty_time)
        diff_status['cell'] = "G{}".format(str(i))

        update_sheet_status(
            light_status=light_status,
            now_status=now_status,
            report_status=report_status,
            diff_status=diff_status
        )
        time.sleep(math.floor(100 / 24))
        # compare current light value with desired light value
        dt = deque(input_from_sheets("B{}".format(str(i))))
        dt_value = dt[0][0]
        print(dt, dt_value)
        analysis = analyze_thresholds({'desired': int(dt_value),
                                       'current': int(light_status['value'])})
        print('device_id: {}, analysis: {}'.format(device_id, analysis))

        # get a timestamp
        now = datetime.datetime.utcnow()
        now = now.strftime("%Y-%m-%d %H:%M:%S")
        cell = 'E{}'.format(str(i))
        # if different, update to desired light value
        if diff_minutes > 32:
            update_sheet_status(
                check_battery={'value': 'CHECK BATTERY', 'cell': cell})
        else:
            if not analysis:
                update_light_value(device_id, dt_value)
                update_sheet_status(
                    light_update={'value': 'attempted {}'.format(now),
                                  'cell': cell})
            else:
                update_sheet_status(light_update={
                    'value': 'verified {}'.format(now),
                    'cell': cell})
        # finally, update the increment var
        time.sleep(math.floor(100 / 24))
        i += 1

    return {'data': data, 'time': report_status['value']}


def update_sheet_status(**kwargs):
    """Bulk update statuses."""
    for k, v in kwargs.items():
        print('k: {}, v: {}'.format(k, v))
        write_to_cell(v.get('value'), v.get('cell'))


def process_device_ids(fix=False):
    """Run the device process."""
    process = {}
    device_ids = get_device_ids()
    for device in device_ids:
        comp = compile_light_time(device)
        process[device] = comp
        if fix is True:
            light = int(process[device].get('light'))
            diff = process[device].get('time difference')

            if light < 50:
                print('{} has threshold of {}. Checking battery status'.format(
                    device, light))
                if diff >= 61:
                    process[device]['update status'] = 'Not updated.'
                    print('''\n
                        Cannot update {}. \n
                        It hasn\'t been online in {} minutes.'''.format(
                        device, diff))
                else:
                    update = update_light_value(device, 50)
                    process[device]['update status'] = 'Update attempted.'
                    print('Updating {}'.format(device))
                    print(update)
            else:
                print('{} is already at {}'.format(device, light))
                if light > 51:
                    print('Setting {} to {}'.format(device, 50))
                    update = update_light_value(device, 50)
                    process[device]['update status'] = 'Update attempted.'
                    print('Updating {}'.format(device))
                    print(update)

    return process

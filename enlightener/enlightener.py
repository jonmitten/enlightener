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
                         get_status_for_device,
                         locate_now,
                         update_light_value)
from google_sheets import (input_from_sheets,
                           write_to_cell)
from settings import SHEET

logger = logging.getLogger('ENLIGHTENER')


def analyze_thresholds(values):
    """
    Take in values, parse rows, compare desired thresholds.

    act accordingly.
    """
    if values['desired'] == values['current']:
        return True
    return False


def get_timestamp(req):
    """Get timestamp from req."""
    timestamp = req.get('statusTimeStamp')

    return timestamp


def get_current_light_reading(req):
    """Get light value from req."""
    current_light_reading = req.get('light')
    return current_light_reading


def get_light_threshold(req):
    """Get light from req."""
    light_threshold = req.get("highlight")

    return light_threshold


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
    light_reading = get_current_light_reading(status)

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
    data = input_from_sheets("{}!A2:B100".format(SHEET))
    i = 2
    light_threshold_status = {}
    now_status = {}
    report_status = {}
    diff_status = {}
    current_light_reading = {}

    print('so now this data is giving me a hard time: {}'.format(data))
    for row in data:
        print('and this row is giving me a hard time: {}'.format(row))
        device_id = row[0]

        """Process a location stamp."""
        print('device_id is: {}'.format(device_id))
        time.sleep(math.floor(100 / 24))
        print("hang on a few seconds")
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

        print("ROW {} IS GIVING ME A PROBLEM: {}".format(
            i, desired_threshold_value))

        # except IndexError as e:
        #     print("index error:{}".format(e))
        print("here are your threshold values, Jon: {} : {}".format(
            light_threshold_status['value'], desired_threshold_value))
        analysis = analyze_thresholds(
            {'desired': int(desired_threshold_value),
             'current': int(light_threshold_status['value'])})
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
            print('''\n\n\n\n\n
                ANALYSIS for {device} with light threshold of {threshold} where {desired} is desired: {analysis}
                \n\n\n\n\n\n\n'''.format(
                device=device_id,
                analysis=analysis,
                threshold=light_threshold_status['value'],
                desired=desired_threshold_value))
            time.sleep(1)
            if not analysis:
                update_light_value(device_id, desired_threshold_value)
                update_sheet_status(
                    light_update={'value': 'attempted {}'.format(now),
                                  'cell': cell})
            else:
                update_sheet_status(light_update={
                    'value': 'verified {}'.format(now),
                    'cell': cell})
        # finally, update the increment var
        print('''\n\n\n\n\n\n\n\n\n\n\n
            let's take a breather...\n\n\n\n\n\n\n\n\n\n\n
            ''')
        time.sleep(math.floor(100 / 24))
        print("back to work!")
        i += 1

    return {'data': data, 'time': report_status['value']}


def update_sheet_status(**kwargs):
    """Bulk update statuses."""
    for k, v in kwargs.items():
        print('k: {}, v: {}'.format(k, v))
        write_to_cell(v.get('value'), v.get('cell'))


# def process_device_ids(fix=False):
#     """Run the device process."""
#     process = {}
#     device_ids = get_device_ids()
#     for device in device_ids:
#         time.sleep(math.floor(100 / 24))
#         comp = compile_light_time(device)
#         process[device] = comp
#         if fix is True:
#             light = int(process[device].get('light'))
#             diff = process[device].get('time difference')

#             if light < 50:
#                 print('{} has threshold of {}. Checking battery status'.format(
#                     device, light))
#                 if diff >= 61:
#                     process[device]['update status'] = 'Not updated.'
#                     print('''\n
#                         Cannot update {}. \n
#                         It hasn\'t been online in {} minutes.'''.format(
#                         device, diff))
#                 else:
#                     update = update_light_value(device, 50)
#                     process[device]['update status'] = 'Update attempted.'
#                     print('Updating {}'.format(device))
#                     print(update)
#             else:
#                 print('{} is already at {}'.format(device, light))
#                 if light > 51:
#                     print('Setting {} to {}'.format(device, 50))
#                     update = update_light_value(device, 50)
#                     process[device]['update status'] = 'Update attempted.'
#                     print('Updating {}'.format(device))
#                     print(update)

#     return process

if __name__ == '__main__':
    update_device_light_thresholds()

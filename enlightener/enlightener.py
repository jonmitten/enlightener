"""
Main module for Enlightener app.

Run this as follows:
"""
import datetime
import logging

from connections import (get_config_for_device,
                         get_device_list,
                         get_status_for_device,
                         update_light_value)
from google_sheets import input_from_sheets

logger = logging.getLogger('ENLIGHTENER')



def analyze_thresholds(values):
    """
    Take in values, parse rows, compare desired thresholds,
    act accordingly.
    """

    for row in values:
        device_id = row[0]
        desired_threshold = row[1]

        current_threshold = get_light_threshold(values)

        # if row[1] is current_threshold:
        #     now = datetime.datetime.now()
        #     update_row(device_id, row[1], light_threshold, now, now)
        # else:
        #     update_row(device_id)


def get_timestamp(req):
    """Get timestamp from req."""
    timestamp = req.get('statusTimeStamp')

    return timestamp

def chop_microseconds(delta):
    return delta - datetime.timedelta(microseconds=delta.microseconds)

def get_time_diff(timestamp, now):

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
        'time': timestamp,
        'light': light,
        'time difference': time_diff,
        'analysis': analysis
    })


def get_device_ids():
    """Get each device from the designated spreadsheet."""
    values = input_from_sheets()
    device_ids = []
    del values[0]
    for x in values:
        device_id = x[0]
        device_ids.append(device_id)
    return device_ids


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

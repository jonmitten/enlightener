"""
Utilities module for Enlightener app.

Moved many of the smaller parsers and formatters
to this utility file to clean up the main
Enlightener module.
"""
import datetime


def now():
    """Get and return a serializable current time."""
    now = datetime.datetime.utcnow()
    now = now.replace(microsecond=0)
    return str(now)


def get_timestamp(resp):
    """Get timestamp from a status request response."""
    timestamp = resp.get('statusTimeStamp')

    return timestamp


def get_current_light_reading(response):
    """Get light value from response."""
    current_light_reading = response.get('light')
    return current_light_reading


def get_light_threshold(response):
    """Get light from response."""
    light_threshold = response.get("highlight")

    return light_threshold


def chop_microseconds(delta):
    """Make deltas without microseconds."""
    return delta - datetime.timedelta(microseconds=delta.microseconds)


def get_time_diff(timestamp, now):
    """Get time delta between two times."""
    now = datetime.datetime.strptime(str(now), '%Y-%m-%d %H:%M:%S')
    try:
        status_time = datetime.datetime.strptime(
            timestamp, '%Y-%m-%d %H:%M:%S')
        minute = datetime.timedelta(seconds=60)
        time_diff = (now - status_time) / minute
        return round(time_diff)
    except ValueError:
        status_time = 'value error for status_time'
        time_diff = status_time
        return time_diff


def analyze_time_diff(diff, device_id):
    """Analyze and return assessement of diff."""
    if diff is 0:
        return "{} last reported {}".format(device_id, 'moments ago')
    return "{} last reported {} minutes ago".format(device_id, diff)


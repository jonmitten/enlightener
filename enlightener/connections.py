"""
Connection manager.

Manage connections to external API.
"""

import math
import requests
import time

from requests.auth import HTTPBasicAuth
from settings import (USERNAME,
                      PASSWORD,
                      BASE_URL,
                      RESOURCES
                      )

basic_credentials = HTTPBasicAuth(USERNAME, PASSWORD)
device_list = RESOURCES['devicelist']
rsrc_config = RESOURCES['getconfig']
rsrc_status = RESOURCES['getstatus']
rsrc_light_set = RESOURCES['putlight']


def build_device_status_url(device_id):
    """
    Get the device status.

    device_id is the remote API identifier for the desired device.
    """
    url = rsrc_status['resource_url']
    query_params = rsrc_status['query_string_parameters']['required'][0]
    tpl_params = (BASE_URL, url, query_params, device_id)
    device_query_url = '{}/{}?{}={}'.format(*tpl_params)

    return device_query_url


def build_device_config_url(device_id):
    """
    Get the device configuration.

    device_id is the remote API identifier for the desiered device.
    """
    url = rsrc_config['resource_url']
    query_params = rsrc_config['query_string_parameters']['required'][0]
    tpl_params = (BASE_URL, url, query_params, device_id)
    device_query_url = '{}/{}?{}={}'.format(*tpl_params)

    return device_query_url


def build_device_list_url(**kwargs):
    """Return a URL for fetching device list."""
    return '{}/{}'.format(BASE_URL, device_list['resource_url'])


def connect_to_api(authenticate=False, options=False):
    """Simple Connect script to ensure API is responsive."""
    auth = basic_credentials if authenticate else ''
    url = build_device_list_url()
    r = requests.get(url, auth=auth)

    return r


def get_device_list(device_list=None, **kwargs):
    """Get all devices from API."""
    if device_list is None:
        auth = basic_credentials
        url = build_device_list_url()
        r = requests.get(url, auth=auth)

        return r.json()


def get_config_for_device(device_id):
    """
    Get and package the json response from remote API.

    device_id is the remote API device identifier for desired device.

    returns JSON of request
    """
    auth = basic_credentials
    url = build_device_config_url(device_id=device_id)
    r = requests.get(url, auth=auth)
    json_r = r.json()

    return json_r


def get_status_for_device(device_id):
    """
    Get and package the JSON response from the API.

    device_id is the remote API device identifier for desired device.

    Returns JSON of request.
    """
    auth = basic_credentials
    url = build_device_status_url(device_id=device_id)
    r = requests.get(url, auth=auth)
    json_r = r.json()

    return json_r


def update_light_value(device_id, threshold):
    """Put an updated value to a device."""
    url = rsrc_light_set['resource_url']
    params = rsrc_light_set['query_string_parameters']
    required = params['required']
    data = {required[0]: device_id, required[1]: threshold}
    auth = basic_credentials

    uri = '{}/{}'.format(BASE_URL, url)

    r = requests.put(uri, params=data, auth=auth)

    if r.status_code is 200:
        return 'success'
    else:
        return 'put failed with error {}'.format(r.status_code)


def locate_now(device_id):
    """Perform location to refresh feed."""
    print("locating {}".format(device_id))
    url = "https://restapi.sendum.com/locatenow?deviceidentifier={}".format(
        device_id)
    r = requests.post(url, auth=basic_credentials)
    print("find now for {} :::: status {}\n\n\n".format(
        device_id, r.status_code))

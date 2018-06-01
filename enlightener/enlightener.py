"""
Main module for Enlightener app.

Run this as follows:
"""
import requests

from requests.auth import HTTPBasicAuth
from settings import USERNAME, PASSWORD, BASE_URL, RESOURCES

username = USERNAME
password = PASSWORD
base_url = BASE_URL
devicelist = RESOURCES['devicelist']

class Enlightener():
    """Main class."""

    def hello(self):
        """Hello world."""
        return 'hello world'

    def connect_to_api(resource, authenticate=False, options=False):
        """Simple Connect script to ensure API is responsive"""
        auth = ''
        if authenticate:
            auth = HTTPBasicAuth(username, password)

        if options:
            # write options logic
            pass

        url = ('{}/{}'.format(base_url, resource['resource_url']))

        r = requests.get(url, auth=auth)
        return r

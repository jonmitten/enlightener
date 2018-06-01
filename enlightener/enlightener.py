"""
Main module for Enlightener app.

Run this as follows:
"""
import requests

from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from requests.auth import HTTPBasicAuth
from settings import USERNAME, PASSWORD, BASE_URL, RESOURCES, SPREADSHEET_ID


basic_credentials = HTTPBasicAuth(USERNAME, PASSWORD)
device_list = RESOURCES['devicelist']

# set up the Sheets API
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
store = file.Storage('credentials.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('../client_secret.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('sheets', 'v4', http=creds.authorize(Http()))


# call the spreadsheets API
RANGE_NAME = 'Sheet1!A1:C100'

def hello_sheets():
    """Proves Sheets API connectivitiy."""
    results = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME).execute()

    values = results.get('values', [])
    if not values:
        print('No data found.')
    else:
        print('PTUnitID', 'Lightthreshold')
        for row in values:
            # print columns A and B, which correspond to indeces 0 and 1
            print('{}, {}'.format(row[0], row[1]))

    return values


def hello():
    """Hello world."""
    return 'hello world'

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
    if device_list is None:
        auth = basic_credentials
        url = build_device_list_url()
        r = requests.get(url, auth=auth)

        return r.json()




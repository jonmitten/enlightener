"""
Google Sheets Python API helper file.

Sets up access to CONSTs and vars.
"""
from settings import SPREADSHEET_ID

from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

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
    """Prove Sheets API connectivitiy."""
    results = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID,
                                                  range=RANGE_NAME).execute()

    values = results.get('values', [])
    if not values:
        print('No data found.')
    return values


def input_from_sheets():
    """Read input from Google Sheet."""
    results = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID,
                                                  range=RANGE_NAME).execute()
    values = results.get('values', [])
    if not values:
        print('No Data Found')
    return values

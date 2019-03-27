"""
Google Sheets Python API helper file.

Sets up access to CONSTs and vars.
"""
import time

from pprint import pprint
from settings import SPREADSHEET_ID, SHEET, RANGE_NAME

from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
# set up the Sheets API
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
store = file.Storage('credentials.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('../client_secret.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('sheets', 'v4', http=creds.authorize(Http()))


# call the spreadsheets API


def hello_sheets():
    """Prove Sheets API connectivitiy."""
    hello_range_name = 'hello_sheet!A2:B1000'
    results = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=hello_range_name).execute()

    values = results.get('values', [])
    if not values:
        print('No data found.')
    return values


def input_from_sheets(range_name=RANGE_NAME, call_from="self"):
    """Read input from Google Sheet."""
    print("ENTER: input_from_sheets({}) called from {}".format(
        RANGE_NAME, call_from))
    results = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID,
                                                  range=RANGE_NAME).execute()
    print("results: {}".format(results))
    values = results.get('values', [])
    print("values: {}".format(values))
    if not values:
        print('No Data Found')
    return values


"""_cell methods map to static spreadsheet columns."""


def light_threshold_status_cell(i):
    """Make and return the light_threhosld_status_cell at column C."""
    return "C{}".format(str(i))


def time_checked_cell(i):
    """Make and return the time_checked aka now_status cell at Column D."""
    return "D{}".format(str(i))


def last_updated_cell(i):
    """Make and return the last_updated cell at Column E."""
    return "E{}".format(str(i))


def report_status_cell(i):
    """Make and return the report_status cell at Column F."""
    return "F{}".format(str(i))


def time_since_last_report_cell(i):
    """Make and return the Time Since Last Report cell at Column G."""
    return "G{}".format(str(i))


def get_col_height(data):
    """Get length of col height."""
    pass


def increase_cell_by_one(cell):
    """Take cell's A1-notation and increment by one col."""
    pass


def decrease_cell_by_one(cell):
    """Take cell's A1-notation and decrement by one col."""
    pass


def update_sheet_status(**kwargs):
    """Bulk update statuses."""
    print("update_sheet_status kwargs: {}".format(kwargs))
    if 'sheet' in kwargs:
        sheet = kwargs.pop('sheet')
        print("your sheet is: {}".format(sheet))
        print("kwargs items: {}".format(kwargs.items()))
        for k, v in kwargs.items():
            print('k : {}, v: {}, sheet: {}'.format(k, v, sheet))
            write_to_cell(v.get('value'), v.get('cell'), sheet)
    else:
        for k, v in kwargs.items():
            print('k: {}, v: {}'.format(k, v))
            write_to_cell(v.get('value'), v.get('cell'))


def write_to_cell(data="Hello from Python!", cell="B6", sheet=SHEET):
    """Write a value to a specific cell using A1 notation."""
    # How the input data should be interpreted.
    value_input_option = 'USER_ENTERED'  # TODO: Update placeholder value.

    range_ = "{}!{}".format(sheet, cell)
    value_range_body = {
        "range": range_,
        "values": [
            [data]
        ]
    }

    request = service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=range_,
        valueInputOption=value_input_option,
        body=value_range_body)

    response = request.execute()

    # TODO: Change code below to process the `response` dict:
    pprint("done writing to cell: {}".format(response))

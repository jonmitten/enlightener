# enlightener
Customized Light Threshold Checker for IoT Devices

## security and testing
In order for the tests to run, a Google Sheets API key and client_secret.json file are required at the project root folder (.gitignored)

Additionally, to keep the project public and secure, a settings.py file should be created by the developer to store sensitive login information, credentials, API text keys, etc. 

Additionally, to obfuscate the type of devices being queried, a devices.json or devices.py file should be created. 

Following this naming convention will allow the developer to keep sensitive information off of the Git repository.

## Google Sheets
The Google Sheets API is used to read and to write to. You will need to register yourself for the Google Sheets API.
https://developers.google.com/sheets/api/quickstart/python


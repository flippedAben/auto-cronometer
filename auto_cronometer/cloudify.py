import os
import os.path
from google.oauth2 import service_account
from googleapiclient.discovery import build

import auto_cronometer.grocery_list as grocery_list

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SHEET_ID = os.environ.get('google_sheets_api_sheet_id')


def get_service():
    credentials = service_account.Credentials.from_service_account_file(
        os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'))
    service = build(
        'sheets',
        'v4',
        credentials=credentials.with_scopes(SCOPES),
        cache_discovery=False)
    return service


def update_groceries(sheet, locked_recipes_yaml):
    """
    Put grocery list data on the cloud.
    """
    print('Updating grocery sheet...')
    sheet_name = 'List'

    data = grocery_list.get_grocery_list(locked_recipes_yaml)
    table = []
    for entry in data.values():
        row = [
            entry['name'],
            entry['amount'],
            entry['unit'],
            entry['group'],
        ]
        table.append(row)

    # Sort by "group"
    table.sort(key=lambda x: x[3])

    # Clear the existing grocery list
    sheet.values().clear(
        spreadsheetId=SHEET_ID,
        range=f'{sheet_name}!A:D',
        body={}
    ).execute()

    # Sort by order
    body = {
        'values': table
    }
    sheet.values().update(
        spreadsheetId=SHEET_ID,
        range=f'{sheet_name}!A1',
        valueInputOption='USER_ENTERED',
        body=body
    ).execute()

    # Auto resize the columns for easier reading
    body = {
        'requests': [
            {
                'autoResizeDimensions': {
                    'dimensions': {
                        'dimension': 'COLUMNS',
                        'startIndex': 0,
                        'endIndex': len(table[0])
                    }
                }
            }
        ]
    }
    sheet.batchUpdate(
        spreadsheetId=SHEET_ID,
        body=body
    ).execute()


def upload_grocery_list(locked_recipes_yaml):
    sheet = get_service().spreadsheets()
    update_groceries(sheet, locked_recipes_yaml)

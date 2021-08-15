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


# TODO move metadata sheet to YAMl file on local computer's config files.
def get_metadata(sheet):
    """
    Retrieve meta data on the groceries.
    """
    sheet_name = 'Metadata'

    result = sheet.values().get(
        spreadsheetId=SHEET_ID,
        range=f'{sheet_name}!A:C',
    ).execute()

    values = result['values']
    metadata = {}
    for i, row in enumerate(values[1:], start=2):
        item = row[0]
        order = row[1]
        # Omitted value implies the item is not in stock
        in_stock = False
        if len(row) == 3:
            in_stock = bool(row[2])
        metadata[item] = [f'={sheet_name}!B{i}', float(order), in_stock]
    return metadata


def update_groceries(sheet, metadata, locked_recipes_yaml):
    """
    Put grocery list data on the cloud.
    """
    print('Updating grocery sheet...')
    sheet_name = 'List'

    # Read the local grocery list from ingredients.csv files
    # Ignore the header
    data = grocery_list.get_grocery_list(locked_recipes_yaml)[1:]

    # Ignore items that are "in stock" (i.e. we already have enough)
    no_metadata_items = []
    out_of_stock_data = []
    for row in data:
        item = row[0]
        if item in metadata:
            if not metadata[item][2]:
                out_of_stock_data.append(row)
        else:
            no_metadata_items.append(item)

    if no_metadata_items:
        print('[Error] Upload failed. These items have no metadata. Add:\n')
        for item in no_metadata_items:
            print(item)
        exit(1)

    # Clear the existing grocery list
    sheet.values().clear(
        spreadsheetId=SHEET_ID,
        range=f'{sheet_name}!A:D',
        body={}
    ).execute()

    # Apply an ordering if it exists
    for row in out_of_stock_data:
        item = row[0]
        if item in metadata:
            row.append(metadata[item][1])

    # Sort by order
    out_of_stock_data.sort(key=lambda x: x[3])
    body = {
        'values': out_of_stock_data
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
                        'endIndex': len(out_of_stock_data[0])
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
    metadata = get_metadata(sheet)
    update_groceries(sheet, metadata, locked_recipes_yaml)

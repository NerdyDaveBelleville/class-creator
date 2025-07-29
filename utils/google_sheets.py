import gspread
from google.oauth2 import service_account
import pandas as pd
import os
from utils.config import CONFIG

def get_google_sheets_credentials():
    """
    Get credentials for Google Sheets API.
    
    Returns:
        Credentials object for Google Sheets API
    """
    # Check if credentials file exists
    creds_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'credentials.json')
    
    if not os.path.exists(creds_path):
        raise FileNotFoundError(
            "credentials.json file not found. Please download the service account key file "
            "from Google Cloud Console and save it as 'credentials.json' in the project root directory."
        )
    
    # Create credentials from service account file
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = service_account.Credentials.from_service_account_file(creds_path, scopes=scope)
    
    return credentials

def extract_sheet_to_dataframe(spreadsheet_id, sheet_name):
    """
    Extract a sheet from Google Sheets to a pandas DataFrame.
    
    Args:
        spreadsheet_id: ID of the Google Sheets document
        sheet_name: Name of the sheet to extract
        
    Returns:
        pandas DataFrame containing the sheet data
    """
    try:
        # Get credentials
        credentials = get_google_sheets_credentials()
        
        # Authorize with gspread
        gc = gspread.authorize(credentials)
        
        # Open the spreadsheet
        spreadsheet = gc.open_by_key(spreadsheet_id)
        
        # Get the specified worksheet
        worksheet = spreadsheet.worksheet(sheet_name)
        
        # Get all values from the worksheet
        data = worksheet.get_all_values()
        
        # Convert to DataFrame
        df = pd.DataFrame(data[1:], columns=data[0])
        
        return df
    
    except Exception as e:
        print(f"Error extracting sheet '{sheet_name}': {str(e)}")
        return pd.DataFrame() 
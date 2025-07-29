import pandas as pd
import os
from utils.config import CONFIG

def extract_reference_data():
    """
    Extract reference data from the spreadsheet and save to CSV files.
    """
    # Get configuration
    spreadsheet_path = CONFIG['data']['spreadsheet_path']
    reference_sheets = CONFIG['data']['reference_sheets']
    data_dir = CONFIG['paths']['data_dir']
    
    # Create data directory if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)
    
    print(f"Loading spreadsheet from {spreadsheet_path}...")
    
    try:
        # Read the reference tabs
        parent_data = pd.read_excel(
            spreadsheet_path, 
            sheet_name=reference_sheets['parent_data']
        )
        
        subject_key = pd.read_excel(
            spreadsheet_path, 
            sheet_name=reference_sheets['subject_key']
        )
        
        grade_lookup = pd.read_excel(
            spreadsheet_path, 
            sheet_name=reference_sheets['grade_lookup']
        )
        
        # Save to CSV files
        parent_data.to_csv(os.path.join(data_dir, 'parent_data.csv'), index=False)
        subject_key.to_csv(os.path.join(data_dir, 'subject_key.csv'), index=False)
        grade_lookup.to_csv(os.path.join(data_dir, 'grade_lookup.csv'), index=False)
        
        print("Reference data extracted and saved to CSV files.")
        return True
    except Exception as e:
        print(f"Error extracting reference data: {str(e)}")
        return False

if __name__ == "__main__":
    extract_reference_data() 
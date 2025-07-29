import json
import os
import pandas as pd
from utils.config import CONFIG

def update_course_master_with_data():
    """
    Update the course_master.json file with actual data from the parent data tab.
    """
    # Path to the course master file
    master_data_path = os.path.join(CONFIG['paths']['data_dir'], 'course_master.json')
    
    # Path to the parent data file (assuming it's a CSV)
    parent_data_path = os.path.join(CONFIG['paths']['data_dir'], 'parent_data.csv')
    
    try:
        # Load existing course master data
        with open(master_data_path, 'r') as f:
            course_master = json.load(f)
        
        # Load parent data
        parent_data = pd.read_csv(parent_data_path)
        
        # Map parent data to course master
        for _, row in parent_data.iterrows():
            slug = row.get('slug', '')
            
            if slug and slug in course_master:
                # Update course with parent data
                course_master[slug] = {
                    'field_0': slug,
                    'field_1': row.get('state', 'Published'),
                    'field_2': row.get('parent', 'Varsity Tutors'),
                    'field_3': row.get('parent_title', ''),
                    'field_4': row.get('item_name', ''),
                    'field_5': row.get('commodity', ''),
                    'field_6': row.get('item_type', ''),
                    'field_7': row.get('field_7', ''),  # Include field_7 even if skipped in UI
                    'field_8': row.get('subject_name', ''),
                    'field_9': row.get('subject_id', ''),
                    'field_10': row.get('content_title', ''),
                    'field_11': row.get('content_description', ''),
                    'field_12': row.get('content_keywords', ''),
                    'field_13': row.get('grades', ''),
                    'field_14': row.get('course_title', ''),
                    'field_15': row.get('business_units', ''),
                    'field_16': row.get('price_dollars', '0'),
                    'field_17': row.get('image_file_name', '')
                }
        
        # Save the updated data
        with open(master_data_path, 'w') as f:
            json.dump(course_master, f, indent=2)
        
        print(f"Successfully updated {len(course_master)} courses in {master_data_path}")
        return True
    
    except Exception as e:
        print(f"Error updating course master data: {str(e)}")
        return False

if __name__ == "__main__":
    update_course_master_with_data() 
import json
import os
from utils.config import CONFIG

def update_course_master():
    """
    Update the course_master.json file to ensure all courses have all 17 fields.
    """
    # Path to the course master file
    master_data_path = os.path.join(CONFIG['paths']['data_dir'], 'course_master.json')
    
    try:
        # Load existing data
        with open(master_data_path, 'r') as f:
            course_master = json.load(f)
        
        # Default values for all fields
        default_values = {
            'field_0': '',  # slug (will be overwritten)
            'field_1': 'Published',  # state
            'field_2': 'Varsity Tutors',  # parent
            'field_3': '',  # parent_title
            'field_4': '',  # item_name
            'field_5': '',  # commodity
            'field_6': '',  # item_type
            'field_7': '',  # (skipped)
            'field_8': '',  # subject_name
            'field_9': '',  # subject_id
            'field_10': '',  # content_title
            'field_11': '',  # content_description
            'field_12': '',  # content_keywords
            'field_13': '',  # grades
            'field_14': '',  # course_title
            'field_15': '',  # business_units
            'field_16': '0',  # price_dollars
            'field_17': ''   # image_file_name
        }
        
        # Update each course to ensure it has all fields
        updated_courses = {}
        for slug, course_data in course_master.items():
            # Start with default values
            updated_course = default_values.copy()
            
            # Set the slug
            updated_course['field_0'] = slug
            
            # Update with existing values
            for field, value in course_data.items():
                updated_course[field] = value
            
            # Add to updated courses
            updated_courses[slug] = updated_course
        
        # Save the updated data
        with open(master_data_path, 'w') as f:
            json.dump(updated_courses, f, indent=2)
        
        print(f"Successfully updated {len(updated_courses)} courses in {master_data_path}")
        return True
    
    except Exception as e:
        print(f"Error updating course master data: {str(e)}")
        return False

if __name__ == "__main__":
    update_course_master() 
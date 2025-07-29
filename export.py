import csv

def generate_csv(course_data, output_file):
    """
    Generate a CSV file from the course data.
    
    Args:
        course_data (dict): Dictionary containing course data.
        output_file (str): Path to the output CSV file.
    """
    # Define CSV headers
    headers = [
        'course_title', 'course_code', 'parent', 'parent_title', 'item_name',
        'commodity', 'item_type', 'business_units', 'subject_name_general',
        'subject_id', 'parent_grade_tags', 'meeting_days', 'parent_course_hours',
        'session_count', 'capacity', 'price_in_dollars', 'content_product_image_link',
        'item_tags'
    ]
    
    # Create a list to store the rows
    rows = []
    
    # Process each course
    for course_slug, course in course_data.items():
        # Get the class type (default to Group Class if not specified)
        class_type = course.get('class_type', 'Group Class')
        
        # Determine the suffix based on class type
        suffix = "LS" if class_type == "Livestream" else "GC"
        
        # Create the course title with the appropriate suffix
        course_title = f"{course.get('field_3', '')} {suffix}"
        
        # Format meeting days properly
        meeting_days = course.get('field_11', '')
        # Format meeting days as a comma-separated list if it's a multi-line string
        if '\n' in meeting_days:
            meeting_days = ', '.join([day.strip() for day in meeting_days.split('\n') if day.strip()])
        
        # Create a row for the CSV
        row = [
            course_title,                      # course_title with LS/GC suffix
            course_slug,                       # course_code
            course.get('field_2', ''),         # parent
            course.get('field_3', ''),         # parent_title
            course.get('field_4', ''),         # item_name
            course.get('field_5', ''),         # commodity
            course.get('field_6', ''),         # item_type
            course.get('field_7', ''),         # business_units
            course.get('field_8', ''),         # subject_name_general
            course.get('field_9', ''),         # subject_id
            ', '.join(course.get('field_10', [])),  # parent_grade_tags
            meeting_days,                      # meeting_days (properly formatted)
            course.get('field_12', ''),        # parent_course_hours
            course.get('field_13', ''),        # session_count
            course.get('field_14', ''),        # capacity
            course.get('field_15', ''),        # price_in_dollars
            course.get('field_16', ''),        # content_product_image_link
            ', '.join(course.get('field_17', []))   # item_tags
        ]
        
        rows.append(row)
    
    # Write to CSV
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    
    print(f"CSV file generated: {output_file}") 
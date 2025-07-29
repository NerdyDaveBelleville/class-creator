import csv
import json
import os

# Path to the CSV file
csv_path = '/Users/dave.belleville/Documents/AI Secret Agents/Class_Creator/data/Untitled spreadsheet - Sheet1.csv'

# Path to the course_master.json file
course_master_path = "Class_Creator/data/course_master.json"

# Dictionary to hold the course data
course_master = {}

# Read the CSV file
try:
    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        # Create a CSV reader
        csv_reader = csv.reader(csvfile)
        
        # Read the header row
        headers = next(csv_reader)
        
        # Process each row in the CSV
        for row in csv_reader:
            # Skip empty rows
            if not row or not row[0]:
                continue
                
            # Get the slug from the first column
            slug = row[0].strip()
            
            # Create a dictionary for this course
            course_data = {}
            
            # Add each field to the course data with both naming conventions
            for i, value in enumerate(row):
                if i < len(headers):  # Ensure we have a header for this column
                    # Add with descriptive header name
                    field_name = headers[i].strip()
                    
                    # Also add with numeric field name for backward compatibility
                    numeric_field_name = f"field_{i}"
                    
                    # If this is a JSON array field (like field_10), parse it
                    if (field_name == "field_10" or numeric_field_name == "field_10") and value.strip().startswith("["):
                        try:
                            parsed_value = json.loads(value)
                            course_data[field_name] = parsed_value
                            course_data[numeric_field_name] = parsed_value
                        except json.JSONDecodeError:
                            print(f"Error parsing JSON for {slug}, field {field_name}: {value}")
                            course_data[field_name] = value
                            course_data[numeric_field_name] = value
                    else:
                        course_data[field_name] = value
                        course_data[numeric_field_name] = value
            
            # Add this course to the master dictionary
            course_master[slug] = course_data
            
except Exception as e:
    print(f"Error reading CSV file: {e}")
    exit(1)

# Save the course_master.json file
try:
    with open(course_master_path, 'w', encoding='utf-8') as f:
        json.dump(course_master, f, indent=2)
    print(f"Successfully created course_master.json with {len(course_master)} courses.")
except Exception as e:
    print(f"Error saving course_master.json: {e}")

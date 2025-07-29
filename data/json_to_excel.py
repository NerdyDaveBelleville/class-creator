import json
import pandas as pd
from pathlib import Path

# Read the JSON file
json_path = Path('/Users/dave.belleville/Documents/AI Secret Agents/Class_Creator/data/course_master.json')
with open(json_path, 'r') as f:
    data = json.load(f)

# Create a list to store the rows
rows = []

# Process each course
for slug, course_data in data.items():
    # Helper function to safely get values
    def get_value(field_name, field_num):
        value = course_data.get(field_name, course_data.get(f'field_{field_num}', ''))
        if isinstance(value, list):
            return ', '.join(str(x) for x in value if x is not None)
        return str(value) if value is not None else ''

    row = {
        'Slug': slug,
        'State': get_value('State', 1),
        'Parent': get_value('Parent', 2),
        'Parent Title': get_value('Parent Title', 3),
        'Item Name': get_value('Item Name', 4),
        'Commodity Type': get_value('Commodity Type', 5),
        'Item Type': get_value('Item Type', 6),
        'Business Units': get_value('Business Units', 7),
        'Subject Name - General': get_value('Subject Name - General', 8),
        'Subject ID': get_value('Subject ID', 9),
        'Parent Grade Tags': get_value('Parent Grade Tags', 10),
        'Days of Week': get_value('Days of Week', 11),
        'Parent Course Hours': get_value('Parent Course Hours', 12),
        'Session Count': get_value('Session Count', 13),
        'Capacity': get_value('Capacity', 14),
        'Price Dollars': get_value('Price Dollars', 15),
        'Content Product Image': get_value('Content Product Image', 16),
        'Item Tags': get_value('Item Tags', 17)
    }
    rows.append(row)

# Create DataFrame
df = pd.DataFrame(rows)

# Save to Excel
output_path = json_path.parent / 'course_master.xlsx'
df.to_excel(output_path, index=False)

print(f"Excel file created at: {output_path}") 
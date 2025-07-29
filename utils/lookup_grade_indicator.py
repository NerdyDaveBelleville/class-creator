import json
import re
import sys

def load_course_master():
    """Load the course_master.json file."""
    try:
        with open('Class_Creator/data/course_master.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading course_master.json: {e}")
        return {}

def load_grade_master():
    """Load the Grade_Master.json file."""
    try:
        with open('Class_Creator/data/Grade_Master.json', 'r') as f:
            data = json.load(f)
            return data
    except Exception as e:
        print(f"Error loading Grade_Master.json: {e}")
        return {}

def get_parent_grade_tags(slug, course_master):
    """Get the parent grade tags for a given slug."""
    course_info = course_master.get(slug, {})
    parent_grade_tags = course_info.get('field_10', [])
    
    # If parent_grade_tags is a string, try to parse it as JSON
    if isinstance(parent_grade_tags, str):
        try:
            parent_grade_tags = json.loads(parent_grade_tags)
        except json.JSONDecodeError:
            pass
    
    return parent_grade_tags

def extract_grade_range(parent_grade_tags):
    """Extract the grade range from parent grade tags."""
    grade_numbers = []
    for tag in parent_grade_tags:
        if isinstance(tag, str):
            # Extract digits from strings like "10th Grade"
            digits = ''.join(c for c in tag if c.isdigit())
            if digits:
                grade_numbers.append(int(digits))
    
    if grade_numbers:
        min_grade = min(grade_numbers)
        max_grade = max(grade_numbers)
        return f"{min_grade}-{max_grade}"
    
    return ""

def get_title_grade_indicator_by_range(grade_range, grade_master):
    """Get the title_grade_indicator for a given grade range."""
    # Print the raw JSON structure around line 290
    print("\nExamining Grade_Master.json structure:")
    
    # Check if grade_master is a list and has enough elements
    if isinstance(grade_master, list):
        print(f"Grade_Master.json has {len(grade_master)} entries")
        
        # Look at entries around index 290 (if available)
        start_idx = max(0, min(290, len(grade_master) - 1) - 5)
        end_idx = min(start_idx + 10, len(grade_master))
        
        for i in range(start_idx, end_idx):
            if i < len(grade_master):
                entry = grade_master[i]
                print(f"Entry {i}: {entry}")
                
                if isinstance(entry, dict):
                    grades = entry.get("grades", "")
                    title_indicator = entry.get("title_grade_indicator", "")
                    print(f"  grades={grades}, title_grade_indicator={title_indicator}")
                    
                    # Check if this entry matches our grade range
                    if grades == grade_range:
                        print(f"  MATCH FOUND: {title_indicator}")
                        return title_indicator
    
    # If we couldn't find a match by direct index, try searching all entries
    print("\nSearching all entries for grade range:", grade_range)
    for i, entry in enumerate(grade_master):
        if isinstance(entry, dict):
            grades = entry.get("grades", "")
            if grades == grade_range:
                title_indicator = entry.get("title_grade_indicator", "")
                print(f"Match found at entry {i}: {title_indicator}")
                return title_indicator
    
    # If still no match, use a hardcoded mapping for common grade ranges
    print("\nUsing hardcoded mapping for grade range:", grade_range)
    hardcoded_mapping = {
        "9-12": "H",
        "6-8": "M",
        "K-5": "E",
        "10-12": "H",
        "11-12": "H"
    }
    
    if grade_range in hardcoded_mapping:
        return hardcoded_mapping[grade_range]
    
    return ""

def main():
    # Load the data files
    course_master = load_course_master()
    grade_master = load_grade_master()
    
    if not course_master:
        print("Error: Could not load course_master.json")
        return
    
    if not grade_master:
        print("Error: Could not load Grade_Master.json")
        return
    
    # Check if a slug was provided as a command-line argument
    if len(sys.argv) > 1:
        slug = sys.argv[1]
    else:
        # Prompt the user for a slug
        slug = input("Enter a course slug: ")
    
    # Get the parent grade tags
    parent_grade_tags = get_parent_grade_tags(slug, course_master)
    print(f"Parent Grade Tags: {parent_grade_tags}")
    
    # Extract the grade range
    grade_range = extract_grade_range(parent_grade_tags)
    print(f"Extracted Grade Range: {grade_range}")
    
    # Get the title grade indicator based on the grade range
    title_grade_indicator = get_title_grade_indicator_by_range(grade_range, grade_master)
    
    # Print the results
    print(f"\nSlug: {slug}")
    print(f"Parent Grade Tags: {parent_grade_tags}")
    print(f"Grade Range: {grade_range}")
    print(f"Title Grade Indicator: {title_grade_indicator}")

if __name__ == "__main__":
    main() 
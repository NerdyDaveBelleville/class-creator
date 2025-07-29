import pandas as pd
import numpy as np
import datetime
import re
import os
import json
from typing import Dict, List, Any, Optional
from utils.config import CONFIG
import streamlit as st

def load_course_master_data():
    """
    Load course master data from JSON file.
    
    Returns:
        Dictionary containing course master data
    """
    master_data_path = os.path.join(CONFIG['paths']['data_dir'], 'course_master.json')
    try:
        with open(master_data_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        log_error("Error loading course data", exc_info=True)
        st.error("We couldn't load the course data. Please check your file or contact an administrator if the problem continues.")
        return {}

def save_course_master_data(data):
    """
    Save course master data to JSON file.
    
    Args:
        data: Dictionary containing course master data
    """
    master_data_path = os.path.join(CONFIG['paths']['data_dir'], 'course_master.json')
    try:
        with open(master_data_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving course master data: {str(e)}")
        return False

def load_grade_master_data():
    """Load grade master data from JSON file."""
    try:
        file_path = os.path.join(CONFIG['paths']['data_dir'], 'Grade_Master.json')
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading Grade_Master.json: {str(e)}")
        return {}

def get_grade_mapping_from_tags(parent_grade_tags, grade_master_data):
    """
    Get the grade mapping value from parent grade tags.
    
    Args:
        parent_grade_tags: List of grade tags (e.g., ["10th Grade", "11th Grade", "12th Grade"])
        grade_master_data: The loaded Grade_Master.json data
        
    Returns:
        The corresponding grade mapping value (e.g., "10|11|12") or empty string if not found
    """
    if not parent_grade_tags:
        return ""
    
    # Handle case where grade_master_data is empty or invalid
    if not grade_master_data or not isinstance(grade_master_data, list):
        # Extract grade numbers and create pipe-separated string
        grade_numbers = []
        tags_to_process = parent_grade_tags if isinstance(parent_grade_tags, list) else [parent_grade_tags]
        
        for tag in tags_to_process:
            if isinstance(tag, str):
                # Extract grade number from strings like "10th Grade"
                if "kindergarten" in tag.lower():
                    grade_numbers.append("k")
                else:
                    # Extract digits from the grade string
                    digits = ''.join(c for c in tag if c.isdigit())
                    if digits:
                        grade_numbers.append(digits)
        
        return "|".join(grade_numbers) if grade_numbers else ""
    
    # Convert parent grade tags to a string representation for comparison
    if isinstance(parent_grade_tags, str):
        tags_str = parent_grade_tags
    else:
        # Sort the tags to ensure consistent comparison
        sorted_tags = sorted(parent_grade_tags)
        tags_str = json.dumps(sorted_tags)
    
    # Look for a matching entry in grade_master_data
    for entry in grade_master_data:
        if not isinstance(entry, dict):
            continue
            
        entry_tags = entry.get("parent_grade_tags", [])
        
        # Convert entry tags to string for comparison
        if isinstance(entry_tags, str):
            entry_tags_str = entry_tags
        else:
            entry_tags_str = json.dumps(sorted(entry_tags))
        
        # Compare the string representations
        if entry_tags_str == tags_str:
            return entry.get("grade_mapping", "")
    
    # If no match found in grade_master_data, fall back to extracting numbers
    return get_grade_mapping_from_tags(parent_grade_tags, None)

def get_title_grade_indicator_from_tags(parent_grade_tags, grade_master_data):
    """
    Get the title_grade_indicator value from parent grade tags.
    
    Args:
        parent_grade_tags: List of grade tags (e.g., ["10th Grade", "11th Grade", "12th Grade"])
        grade_master_data: The loaded Grade_Master.json data
        
    Returns:
        The corresponding title_grade_indicator value (e.g., "H") or empty string if not found
    """
    if not parent_grade_tags:
        return ""
    
    # Convert parent_grade_tags to a string for comparison if it's already a string
    if isinstance(parent_grade_tags, str):
        try:
            # Try to parse it as JSON
            parent_grade_tags = json.loads(parent_grade_tags)
        except json.JSONDecodeError:
            # If it's not valid JSON, keep it as a string
            pass
    
    # If parent_grade_tags is a list, convert it to a set of strings for comparison
    if isinstance(parent_grade_tags, list):
        parent_tags_set = set(str(tag).lower() for tag in parent_grade_tags)
    else:
        # If it's not a list, create a set with just this item
        parent_tags_set = {str(parent_grade_tags).lower()}
    
    # Look for an exact match in grade_master_data
    for entry in grade_master_data:
        entry_tags = entry.get("parent_grade_tags", [])
        
        # Convert entry_tags to a string for comparison if it's already a string
        if isinstance(entry_tags, str):
            try:
                # Try to parse it as JSON
                entry_tags = json.loads(entry_tags)
            except json.JSONDecodeError:
                # If it's not valid JSON, keep it as a string
                pass
        
        # If entry_tags is a list, convert it to a set of strings for comparison
        if isinstance(entry_tags, list):
            entry_tags_set = set(str(tag).lower() for tag in entry_tags)
        else:
            # If it's not a list, create a set with just this item
            entry_tags_set = {str(entry_tags).lower()}
        
        # Check if the sets are equal
        if parent_tags_set == entry_tags_set:
            return entry.get("title_grade_indicator", "")
    
    # If no exact match, try to find a match based on the grade range
    # Extract grade numbers from parent_grade_tags
    grade_numbers = []
    for tag in parent_tags_set:
        # Extract digits from strings like "10th grade"
        digits = ''.join(c for c in tag if c.isdigit())
        if digits:
            grade_numbers.append(int(digits))
    
    if grade_numbers:
        min_grade = min(grade_numbers)
        max_grade = max(grade_numbers)
        
        # Look for entries in grade_master_data with matching grade ranges
        for entry in grade_master_data:
            grades = entry.get("grades", "")
            # Check if grades is in format like "10-12"
            match = re.match(r'(\d+)-(\d+)', grades)
            if match:
                range_min = int(match.group(1))
                range_max = int(match.group(2))
                
                # Check if our grade range falls within this entry's range
                if min_grade >= range_min and max_grade <= range_max:
                    return entry.get("title_grade_indicator", "")
    
    return ""

def process_class_data(approved_requests: pd.DataFrame) -> pd.DataFrame:
    """
    Process approved class requests using course master data.
    
    Args:
        approved_requests: DataFrame containing approved class requests
        
    Returns:
        DataFrame formatted for bulk upload with the required columns
    """
    # Load course master data
    course_master = load_course_master_data()
    
    # Load grade master data
    grade_master_data = load_grade_master_data()
    
    # Define the exact columns needed for the output CSV
    columns = [
        'slug', 'meeting_days', 'start_date', 'end_date', 'excluded_meeting_dates',
        'meeting_start_time', 'time_zone', 'parent', 'state', 'product_type',
        'subject_name', 'subject_id', 'content.meta.title', 'content.meta.description',
        'content.meta.keywords', 'grades', 'course_title', 'meeting_duration',
        'duration_hours', 'capacity', 'instructor_name', 'rate_type', 'business_units',
        'price_dollars', 'IMAGE file name', 'sponsor_client_id', 'sponsor_waiting_room',
        'sponsor_price_dollars'
    ]
    
    processed_data = pd.DataFrame(columns=columns)
    
    # For each approved request
    for _, request in approved_requests.iterrows():
        # Extract base data from the request
        slug = request['slug']
        meeting_days_str = request['meeting_days']
        start_date = request['start_date']
        end_date = request['end_date']
        start_time = request['start_time']
        
        # Format meeting days for the output (Monday,Wednesday,Friday -> mon|wed|fri)
        meeting_days_formatted = direct_format_meeting_days(meeting_days_str)
        
        # Format dates in YYYY-MM-DD format
        start_date_formatted = format_date(start_date)
        end_date_formatted = format_date(end_date)
        
        # Format time for the output (HH:MM AM/PM)
        meeting_start_time = format_time(start_time)
        
        # Calculate meeting duration (default 60 minutes)
        meeting_duration = CONFIG['defaults']['default_duration_minutes']
        duration_hours = meeting_duration / 60
        
        # DIRECT APPROACH: Filter excluded meeting dates
        excluded_meeting_dates = request.get('excluded_meeting_dates', '')
        
        # Convert to list of date objects
        excluded_dates_list = []
        if isinstance(excluded_meeting_dates, str) and excluded_meeting_dates.strip():
            for date_str in excluded_meeting_dates.split(','):
                try:
                    date_obj = datetime.datetime.strptime(date_str.strip(), '%Y-%m-%d').date()
                    excluded_dates_list.append(date_obj)
                except ValueError:
                    continue
        
        # Get meeting days as list
        meeting_days_list = meeting_days_str.split(',')
        
        # Filter dates that match meeting days and are within range
        filtered_dates = []
        for date_obj in excluded_dates_list:
            if start_date <= date_obj <= end_date:
                day_name = date_obj.strftime('%A')
                if day_name in meeting_days_list:
                    filtered_dates.append(date_obj.strftime('%Y-%m-%d'))
                    print(f"Including {date_obj.strftime('%Y-%m-%d')} ({day_name})")
                else:
                    print(f"Excluding {date_obj.strftime('%Y-%m-%d')} ({day_name}) - not a meeting day")
        
        # Join filtered dates
        filtered_excluded_dates = ','.join(filtered_dates)
        
        # Get course data from master data if available, otherwise generate from slug
        if slug in course_master:
            course_data = course_master[slug]
            subject_name = course_data.get('field_8', '')
            subject_id = course_data.get('field_9', '')
            
            # Use field_3 for all three content meta fields
            content_field = course_data.get('field_3', '')
            content_title = content_field
            content_description = content_field
            content_keywords = content_field
            
            grades = course_data.get('field_13', '')
            course_title = course_data.get('field_14', '')
            business_units = course_data.get('field_7', '')
            price_dollars = course_data.get('field_15', '0')
            image_file_name = course_data.get('field_16', '')
            parent = course_data.get('field_2', 'Varsity Tutors')
            state = course_data.get('field_1', 'Published')
        else:
            # Parse slug to extract information
            slug_info = parse_slug(slug)
            
            # Generate data from slug
            subject_name = slug_info['subject']
            subject_id = get_subject_id(subject_name)
            
            # Default content fields when course not in master data
            content_title = f"{slug_info['brand'].upper()} {subject_name} for {slug_info['grade']}"
            content_description = content_title
            content_keywords = content_title
            
            # Use standardized grade mapping
            grades = slug_info['grade_mapping']
            course_title = f"{subject_name} for {slug_info['grade']}"
            business_units = get_business_unit(slug_info['brand'])
            price_dollars = '0'
            image_file_name = ''
            parent = 'Varsity Tutors'
            state = 'Published'
        
        # Get parent grade tags from field_10
        parent_grade_tags = course_data.get('field_10', [])
        
        # Get the grade mapping from parent grade tags
        grade_mapping = get_grade_mapping_from_tags(parent_grade_tags, grade_master_data)
        
        # Get the title_grade_indicator from field_4 (example item name)
        field4 = course_data.get('field_4', '')
        title_grade_indicator = extract_title_grade_indicator_from_field4(field4)
        
        # Build the course_title according to the formula
        # 1. Use the Parent Title (field_3) from course_master.json
        course_name = course_data.get('field_3', '')
        
        # 2. Format the date (mmdd)
        formatted_date = format_date_mmdd(start_date_formatted)
        
        # 3. Extract the hour
        hour = extract_hour(meeting_start_time)
        
        # 4. Use the title_grade_indicator extracted from field_4
        
        # 5. Determine class type suffix using the stored class_type from request
        class_type = request.get('class_type', 'Group Class')  # Default to Group Class if not specified
        type_suffix = "LS" if class_type == "Livestream" else "GC"
        
        # Combine all parts to create the course_title
        course_title = f"{course_name} {formatted_date}{hour}{title_grade_indicator}{type_suffix}"
        
        # Add duration hours from field_12 (parent course hours)
        duration_hours = course_data.get('field_12', '')
        
        # Add capacity from field_14 (capacity)
        capacity = course_data.get('field_14', '')
        
        # Add rate type from field_6 (item type)
        rate_type = course_data.get('field_6', '')
        
        # Add business units from field_7 with pipe separator
        business_units = course_data.get('field_7', '')
        business_units_formatted = format_business_units(business_units)
        
        # Create a row for the processed data
        row_data = {
            'slug': slug,
            'meeting_days': meeting_days_formatted,
            'start_date': start_date_formatted,
            'end_date': end_date_formatted,
            'excluded_meeting_dates': filtered_excluded_dates,
            'meeting_start_time': meeting_start_time,
            'time_zone': 'America/Chicago',
            'parent': parent,
            'state': state,
            'product_type': 'small_group',
            'subject_name': subject_name,
            'subject_id': subject_id,
            'content.meta.title': content_title,
            'content.meta.description': content_description,
            'content.meta.keywords': content_keywords,
            'grades': grade_mapping,
            'course_title': course_title,
            'meeting_duration': str(meeting_duration),
            'duration_hours': duration_hours,
            'capacity': capacity,
            'instructor_name': '',
            'rate_type': rate_type,
            'business_units': business_units_formatted,
            'price_dollars': price_dollars,
            'IMAGE file name': image_file_name,
            'sponsor_client_id': '',
            'sponsor_waiting_room': '',
            'sponsor_price_dollars': ''
        }
        
        # Add to processed data
        processed_data = pd.concat([processed_data, pd.DataFrame([row_data])], ignore_index=True)
    
    return processed_data

def parse_slug(slug: str) -> Dict[str, str]:
    """
    Parse a slug to extract brand, subject, and grade information.
    
    Args:
        slug: Course code (e.g., "vtgsc-math-grade-6")
        
    Returns:
        Dictionary containing brand, subject, and grade information
    """
    # More flexible pattern matching
    parts = slug.split('-')
    
    if len(parts) < 2:
        return {
            'brand': slug,
            'subject': 'Unknown',
            'grade': 'Unknown'
        }
    
    # Extract brand (first part)
    brand = parts[0]
    
    # Try to extract grade from the end
    grade_parts = []
    subject_parts = []
    
    # Look for grade indicators
    for part in parts[1:]:
        if part.isdigit() or part in ['k', 'K'] or part == 'adult':
            grade_parts.append(part)
        else:
            subject_parts.append(part)
    
    # If we found grade parts, join them
    if grade_parts:
        grade = ' '.join(grade_parts)
        # Format grade nicely
        if grade.lower() == 'k':
            grade = 'Kindergarten'
        elif grade == 'adult':
            grade = 'Adult'
        else:
            try:
                # Try to format as a grade range
                if '-' in grade:
                    start, end = grade.split('-')
                    grade = f"Grades {start}-{end}"
                else:
                    grade = f"Grade {grade}"
            except:
                pass
    else:
        # Default grade if none found
        grade = 'All Grades'
    
    # Join remaining parts as subject
    subject = ' '.join(subject_parts).title()
    
    return {
        'brand': brand,
        'subject': subject,
        'grade': grade
    }

def direct_format_meeting_days(days_str: str) -> str:
    """
    Format meeting days string for the output CSV using a direct approach.
    
    Args:
        days_str: Comma-separated list of meeting days (e.g., "Monday,Wednesday,Friday")
        
    Returns:
        Formatted meeting days string (e.g., "mon|wed|fri")
    """
    # Direct mapping approach - look for specific day names in the string
    result = []
    
    if not isinstance(days_str, str):
        return ""
        
    days_str = days_str.lower()
    
    # Check for each day directly
    if "monday" in days_str:
        result.append("mon")
    if "tuesday" in days_str:
        result.append("tue")
    if "wednesday" in days_str:
        result.append("wed")
    if "thursday" in days_str:
        result.append("thu")
    if "friday" in days_str:
        result.append("fri")
    if "saturday" in days_str:
        result.append("sat")
    if "sunday" in days_str:
        result.append("sun")
    
    # Join with pipe character
    return "|".join(result)

def format_time(time_obj) -> str:
    """
    Format time object for the output CSV.
    
    Args:
        time_obj: Time object
        
    Returns:
        Formatted time string (e.g., "3:30 PM")
    """
    if isinstance(time_obj, datetime.time):
        return time_obj.strftime("%I:%M %p").lstrip('0')
    
    # If already a string, return as is
    return time_obj

def format_date(date_obj):
    """
    Format date object to YYYY-MM-DD string.
    
    Args:
        date_obj: Date object to format
        
    Returns:
        Formatted date string (YYYY-MM-DD)
    """
    if isinstance(date_obj, datetime.date):
        return date_obj.strftime('%Y-%m-%d')
    return str(date_obj)

def get_subject_id(subject: str) -> str:
    """
    Get subject ID based on subject name.
    
    Args:
        subject: Subject name
        
    Returns:
        Subject ID
    """
    # Map common subjects to IDs
    subject_map = {
        'Math': 'MATH',
        'Mathematics': 'MATH',
        'Algebra': 'MATH-ALG',
        'Geometry': 'MATH-GEO',
        'Science': 'SCI',
        'Biology': 'SCI-BIO',
        'Chemistry': 'SCI-CHEM',
        'Physics': 'SCI-PHYS',
        'English': 'ENG',
        'Reading': 'ENG-READ',
        'Writing': 'ENG-WRIT',
        'History': 'HIST',
        'Social Studies': 'SOC',
        'Art': 'ART',
        'Music': 'MUS',
        'Computer Science': 'CS',
        'Programming': 'CS-PROG',
        'Foreign Language': 'LANG',
        'Spanish': 'LANG-SPA',
        'French': 'LANG-FRE'
    }
    
    # Try to find a match, otherwise use a generic ID
    for key, value in subject_map.items():
        if key.lower() in subject.lower():
            return value
    
    # If no match found, create a generic ID from the first 4 letters
    return subject.replace(' ', '').upper()[:4]

def get_business_unit(brand: str) -> str:
    """
    Get business unit based on brand code.
    
    Args:
        brand: Brand code (e.g., "vtgsc", "vtp")
        
    Returns:
        Business unit
    """
    brand_map = {
        'vtgsc': 'Varsity Tutors Global Study Center',
        'vtp': 'Varsity Tutors Platform',
        'vtpsg': 'Varsity Tutors Private School Group',
        'vtsaz': 'Varsity Tutors School Acceleration Zone'
    }
    
    return brand_map.get(brand.lower(), 'Varsity Tutors')

def get_course_info(slug: str, parent_data: pd.DataFrame) -> Dict[str, Any]:
    """
    Get course information from parent data.
    
    Args:
        slug: Course code
        parent_data: DataFrame containing parent course data
        
    Returns:
        Dictionary containing course information
    """
    # Find the row in parent_data that matches the slug
    course_row = parent_data[parent_data['Course Code'] == slug]
    
    if course_row.empty:
        return {}
    
    # Convert the row to a dictionary
    course_info = course_row.iloc[0].to_dict()
    
    return course_info

def generate_course_code(slug_info: Dict[str, Any], subject_key: pd.DataFrame) -> str:
    """
    Generate the course code based on slug information and subject key.
    
    Args:
        slug_info: Dictionary containing parsed slug information
        subject_key: DataFrame containing subject reference data
        
    Returns:
        Formatted course code
    """
    # Example implementation - adjust based on your actual formula
    subject = slug_info.get('subject', '')
    course_number = slug_info.get('course_number', '')
    grade = slug_info.get('grade', '')
    term = slug_info.get('term', '')
    
    # Look up the subject code if needed
    subject_code = subject
    if not subject_key.empty:
        subject_match = subject_key[subject_key['Subject'] == subject]
        if not subject_match.empty:
            subject_code = subject_match.iloc[0].get('Code', subject)
    
    # Format according to your requirements
    return f"{subject_code}{course_number}-G{grade}-{term}"

def generate_course_name(slug_info: Dict[str, Any], parent_data: pd.DataFrame) -> str:
    """
    Generate the course name based on slug information and parent data.
    
    Args:
        slug_info: Dictionary containing parsed slug information
        parent_data: DataFrame containing parent course data
        
    Returns:
        Formatted course name
    """
    # Example implementation - adjust based on your actual formula
    subject = slug_info.get('subject', '')
    grade = slug_info.get('grade', '')
    
    # Look up the full subject name if needed
    subject_name = subject
    if not parent_data.empty:
        subject_match = parent_data[parent_data['Subject Code'] == subject]
        if not subject_match.empty:
            subject_name = subject_match.iloc[0].get('Subject Name', subject)
    
    # Format according to your requirements
    return f"{subject_name} for Grade {grade}"

def generate_course_description(slug_info: Dict[str, Any], parent_data: pd.DataFrame) -> str:
    """
    Generate the course description based on slug information and parent data.
    
    Args:
        slug_info: Dictionary containing parsed slug information
        parent_data: DataFrame containing parent course data
        
    Returns:
        Course description
    """
    # Example implementation - adjust based on your actual formula
    subject = slug_info.get('subject', '')
    
    # Look up the description if available
    if not parent_data.empty:
        subject_match = parent_data[parent_data['Subject Code'] == subject]
        if not subject_match.empty:
            return subject_match.iloc[0].get('Description', '')
    
    # Default description if not found
    return f"Course description for {subject}"

def get_course_image(subject: str, parent_data: pd.DataFrame, default_image: str) -> str:
    """
    Get the course image URL based on subject.
    
    Args:
        subject: Subject code
        parent_data: DataFrame containing parent course data
        default_image: Default image URL if not found
        
    Returns:
        Image URL
    """
    # Example implementation - adjust based on your actual formula
    if not parent_data.empty:
        subject_match = parent_data[parent_data['Subject Code'] == subject]
        if not subject_match.empty:
            return subject_match.iloc[0].get('Image URL', default_image)
    
    # Default image if not found
    return default_image

def get_subject(subject_code: str, subject_key: pd.DataFrame) -> str:
    """
    Get the full subject name based on subject code.
    
    Args:
        subject_code: Subject code from slug
        subject_key: DataFrame containing subject reference data
        
    Returns:
        Full subject name
    """
    # Example implementation - adjust based on your actual formula
    if not subject_key.empty:
        subject_match = subject_key[subject_key['Code'] == subject_code]
        if not subject_match.empty:
            return subject_match.iloc[0].get('Subject', subject_code)
    
    return subject_code

def get_grade(grade: str, grade_lookup: pd.DataFrame) -> str:
    """
    Get the formatted grade based on grade code.
    
    Args:
        grade: Grade code from slug
        grade_lookup: DataFrame containing grade reference data
        
    Returns:
        Formatted grade
    """
    # Example implementation - adjust based on your actual formula
    if not grade_lookup.empty:
        grade_match = grade_lookup[grade_lookup['Grade Code'] == grade]
        if not grade_match.empty:
            return grade_match.iloc[0].get('Grade Display', grade)
    
    return grade

def format_meeting_days(days_list: List[str]) -> str:
    """
    Format meeting days according to required format.
    
    Args:
        days_list: List of day abbreviations
        
    Returns:
        Formatted meeting days string
    """
    # Example implementation - adjust based on your actual formula
    # This might need to convert from 3-letter abbreviations to full names or other formats
    day_mapping = {
        'Mon': 'Monday',
        'Tue': 'Tuesday',
        'Wed': 'Wednesday',
        'Thu': 'Thursday',
        'Fri': 'Friday',
        'Sat': 'Saturday',
        'Sun': 'Sunday'
    }
    
    full_days = [day_mapping.get(day, day) for day in days_list]
    return ', '.join(full_days)

def calculate_end_time(start_time: datetime.time, duration_minutes: int) -> datetime.time:
    """
    Calculate end time based on start time and duration.
    
    Args:
        start_time: Start time
        duration_minutes: Duration in minutes
        
    Returns:
        End time
    """
    # Convert to datetime for easy addition
    start_datetime = datetime.datetime.combine(datetime.date.today(), start_time)
    end_datetime = start_datetime + datetime.timedelta(minutes=duration_minutes)
    return end_datetime.time()

def get_instructor_email(slug_info: Dict[str, Any], parent_data: pd.DataFrame) -> str:
    """
    Get instructor email based on slug information.
    
    Args:
        slug_info: Dictionary containing parsed slug information
        parent_data: DataFrame containing parent course data
        
    Returns:
        Instructor email
    """
    # Example implementation - adjust based on your actual formula
    subject = slug_info.get('subject', '')
    
    if not parent_data.empty:
        subject_match = parent_data[parent_data['Subject Code'] == subject]
        if not subject_match.empty:
            return subject_match.iloc[0].get('Instructor Email', '')
    
    # Default if not found
    return "instructor@example.com"

def get_max_enrollments(slug_info: Dict[str, Any], default_max: int) -> int:
    """
    Get maximum enrollments based on slug information.
    
    Args:
        slug_info: Dictionary containing parsed slug information
        default_max: Default maximum enrollments
        
    Returns:
        Maximum enrollments
    """
    # Example implementation - adjust based on your actual formula
    # This might be a standard value or based on course type
    return default_max

def get_price(slug_info: Dict[str, Any], parent_data: pd.DataFrame, default_price: float) -> float:
    """
    Get price based on slug information.
    
    Args:
        slug_info: Dictionary containing parsed slug information
        parent_data: DataFrame containing parent course data
        default_price: Default price if not found
        
    Returns:
        Price
    """
    # Example implementation - adjust based on your actual formula
    subject = slug_info.get('subject', '')
    
    if not parent_data.empty:
        subject_match = parent_data[parent_data['Subject Code'] == subject]
        if not subject_match.empty:
            return subject_match.iloc[0].get('Price', default_price)
    
    # Default if not found
    return default_price

def format_date_mmdd(date_str):
    """Format a date string as 'mmdd'."""
    try:
        # Parse the date string
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        # Format as 'mmdd'
        return date_obj.strftime('%m%d')
    except Exception as e:
        print(f"Error formatting date: {e}")
        return ""

def extract_hour(time_str):
    """Extract the hour part from a time string."""
    try:
        # Find the position of the colon
        colon_pos = time_str.find(':')
        if colon_pos > 0:
            # Extract everything before the colon
            return time_str[:colon_pos]
        return time_str
    except Exception as e:
        print(f"Error extracting hour: {e}")
        return ""

def extract_title_grade_indicator_from_field4(field4):
    """
    Extract the title_grade_indicator from field_4 (example item name).
    The title_grade_indicator is the letters that immediately follow the numbers in the string.
    
    Examples:
    - "Hola! Let's Learn Spanish (Grades K-1) 01223K" -> "K"
    - "Bridging the Gap in 5th Grade Reading & Writing 01166M" -> "M"
    - "Bridging the Gap in 2nd Grade Math 01174EE" -> "EE"
    
    Args:
        field4: The example item name from field_4
        
    Returns:
        The title_grade_indicator or empty string if not found
    """
    if not field4:
        return ""
    
    # Find the last sequence of digits followed by letters at the end of the string
    match = re.search(r'\d+([A-Z]+)$', field4)
    if match:
        return match.group(1)  # Return the captured letters
    
    return ""

def format_business_units(business_units):
    """
    Format business units by replacing commas with pipes.
    
    Args:
        business_units: The business units string with comma separators
        
    Returns:
        The business units string with pipe separators
    """
    if not business_units:
        return ""
    
    # Replace commas with pipes
    return business_units.replace(',', '|')

def approve_request(request_data: Dict[str, Any]) -> bool:
    """
    Approve a class request.
    
    Args:
        request_data: Dictionary containing request data
        
    Returns:
        True if the request is approved, False otherwise
    """
    try:
        # Process the request
        # ... (existing code)
        return True
    except Exception as e:
        log_error("Error approving request", exc_info=True)
        st.error("There was a problem approving this request. Please try again or contact your admin if the issue persists.")
        return False 
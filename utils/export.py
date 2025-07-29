import os
import pandas as pd
import datetime
import re

def export_to_csv(data: pd.DataFrame, export_dir: str) -> str:
    """
    Export processed data to CSV file with two sections.
    
    Args:
        data: DataFrame containing processed data
        export_dir: Directory to save the CSV file
        
    Returns:
        Path to the exported CSV file
    """
    # Create export directory if it doesn't exist
    os.makedirs(export_dir, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"class_bulk_upload_{timestamp}.csv"
    filepath = os.path.join(export_dir, filename)
    
    # Make a copy of the data to avoid modifying the original
    export_data = data.copy()
    
    # Add static values for sponsor fields
    export_data['sponsor_client_id'] = 0
    export_data['sponsor_price_dollars'] = 0
    
    # Ensure meeting_days is properly formatted
    if 'meeting_days' in export_data.columns:
        # Define a function to properly format the meeting days
        def format_days(day_str):
            # Direct mapping approach - look for specific day names in the string
            result = []
            
            if not isinstance(day_str, str):
                return ""
                
            day_str = day_str.lower()
            
            # Check for each day directly
            if "monday" in day_str or "mon" in day_str:
                result.append("mon")
            if "tuesday" in day_str or "tue" in day_str:
                result.append("tue")
            if "wednesday" in day_str or "wed" in day_str:
                result.append("wed")
            if "thursday" in day_str or "thu" in day_str:
                result.append("thu")
            if "friday" in day_str or "fri" in day_str:
                result.append("fri")
            if "saturday" in day_str or "sat" in day_str:
                result.append("sat")
            if "sunday" in day_str or "sun" in day_str:
                result.append("sun")
            
            # Join with pipe character
            return "|".join(result)
        
        # Apply the formatting function
        export_data['meeting_days'] = export_data['meeting_days'].apply(format_days)
    
    def get_month_name(date_str):
        """Convert date to month name"""
        date_obj = pd.to_datetime(date_str)
        return date_obj.strftime("%B")
    
    def get_day(date_str):
        """Get day of month"""
        date_obj = pd.to_datetime(date_str)
        return str(date_obj.day)
    
    def format_days_for_title(days_str):
        """Format days for title (mon -> Monday, etc.)"""
        day_mapping = {
            'mon': 'Monday',
            'tue': 'Tuesday',
            'wed': 'Wednesday',
            'thu': 'Thursday',
            'fri': 'Friday',
            'sat': 'Saturday',
            'sun': 'Sunday'
        }
        if not days_str:
            return ""
        days = days_str.split('|')
        return '/'.join(day_mapping.get(day.lower(), day) for day in days)
    
    def generate_title(row):
        """Generate title based on the complex logic"""
        course_name = row['content.meta.title']
        
        # Calculate total sessions
        duration_hours = float(row['duration_hours'])
        meeting_duration_hours = float(row['meeting_duration']) / 60  # Convert minutes to hours
        total_sessions = int(duration_hours / meeting_duration_hours)
        
        # Get date components
        month = get_month_name(row['start_date'])
        day = get_day(row['start_date'])
        
        # Format for date-based title
        date_format = f"{month} {day}"
        
        # Format for day-based title
        days_format = format_days_for_title(row['meeting_days'])
        
        # Apply the logic
        if total_sessions == 1 or \
           (total_sessions >= 4 and total_sessions <= 5) or \
           'ISEE' in course_name or 'SSAT' in course_name:
            return f"{course_name} – {date_format} Group"
        else:
            return f"{course_name} – {days_format} Group"
    
    def get_template_id(row):
        """Determine template ID based on course title and duration"""
        # Use the original course_title from the data
        course_title = row['course_title'].lower()  # Use existing course_title field
        meeting_duration = float(row['meeting_duration'])  # in minutes
        
        # Calculate total sessions
        duration_hours = float(row['duration_hours'])
        meeting_duration_hours = meeting_duration / 60
        total_sessions = int(duration_hours / meeting_duration_hours)
        
        # Check conditions in order
        if "lsat proctored" in course_title and meeting_duration == 180:
            return "77386caeed73"
        elif "sat proctored" in course_title:
            return "2c0b0f64b5ca"
        elif "act proctored" in course_title:
            return "a572c93cbaf6"
        elif "gc" in course_title:
            return "7de404c0a50a"
        elif "ls" in course_title and total_sessions == 1:
            return "8a90329c07bf"
        elif "ls" in course_title and total_sessions > 1:
            return "bec6b6228a69"
        else:
            return ""
    
    def get_reocurrence(row):
        """Determine if meeting is one time or recurring"""
        duration_hours = float(row['duration_hours'])
        meeting_duration_hours = float(row['meeting_duration']) / 60  # Convert minutes to hours
        total_sessions = int(duration_hours / meeting_duration_hours)
        
        return "one time" if total_sessions == 1 else "Recurring"
    
    def get_cadence(row):
        """Determine cadence based on reocurrence"""
        duration_hours = float(row['duration_hours'])
        meeting_duration_hours = float(row['meeting_duration']) / 60
        total_sessions = int(duration_hours / meeting_duration_hours)
        
        # If one-time session (same logic as reocurrence)
        return "" if total_sessions == 1 else "weekly"
    
    def get_live_event_experience(row):
        course_title = row['course_title']
        if "GC" in course_title.upper():
            return "interactive"
        else:
            return "webcast"
    
    # Create the second section DataFrame
    bm_headers = [
        'Type', 'Title', 'Purpose', 'Template', 'Reocurrence', 'Cadence', 'Days',
        'Start Date', 'End Date', 'Skip Date', 'Time', 'Duration',
        'Sessions to Generate', 'Timezone',
        'Limit number of session to show on landing page to', 'Allow Registration',
        'Live Event Experience', 'Audience Room Layout', 'Privacy', 'Presenter',
        'Course Name'
    ]
    
    # Create BM upload data
    bm_data = pd.DataFrame(columns=bm_headers)
    
    # Add as many rows as in the original data
    num_rows = len(export_data)
    bm_data['Type'] = ['LiveWebinar'] * num_rows
    bm_data['Title'] = export_data.apply(generate_title, axis=1)
    bm_data['Purpose'] = ''  # Empty as specified
    bm_data['Template'] = export_data.apply(get_template_id, axis=1)
    bm_data['Reocurrence'] = export_data.apply(get_reocurrence, axis=1)
    bm_data['Cadence'] = export_data.apply(get_cadence, axis=1)
    bm_data['Days'] = export_data['meeting_days']  # Just use the existing formatted meeting_days
    bm_data['Start Date'] = export_data['start_date']
    bm_data['End Date'] = export_data['end_date']
    bm_data['Skip Date'] = export_data['excluded_meeting_dates']
    bm_data['Time'] = export_data['meeting_start_time']
    bm_data['Duration'] = export_data['meeting_duration']
    
    def get_sessions_to_generate(row):
        duration_hours = float(row['duration_hours'])
        meeting_duration_hours = float(row['meeting_duration']) / 60
        return int(duration_hours / meeting_duration_hours)
    
    bm_data['Sessions to Generate'] = export_data.apply(get_sessions_to_generate, axis=1)
    
    bm_data['Timezone'] = 'Central Time (US & Canada)'
    bm_data['Limit number of session to show on landing page to'] = 1
    bm_data['Allow Registration'] = 'Until Duration of the class'
    
    bm_data['Live Event Experience'] = export_data.apply(get_live_event_experience, axis=1)
    
    bm_data['Audience Room Layout'] = 'classic'
    bm_data['Privacy'] = 'private'
    bm_data['Presenter'] = ''
    bm_data['Course Name'] = export_data['course_title']
    
    # Write both sections to the CSV file
    with open(filepath, 'w', encoding='utf-8') as f:
        # Write first section
        export_data.to_csv(f, index=False)
        
        # Add 5 blank lines
        f.write('\n' * 5)
        
        # Write second section
        bm_data.to_csv(f, index=False)
    
    return filepath

def save_to_history(requests: pd.DataFrame, history_dir: str):
    """
    Save all processed requests to a history file.
    
    Args:
        requests: DataFrame containing all requests
        history_dir: Directory to save the history file
    """
    # Create history directory if it doesn't exist
    os.makedirs(history_dir, exist_ok=True)
    
    # Generate filename with date
    date = datetime.datetime.now().strftime("%Y%m%d")
    filename = f"class_requests_history_{date}.csv"
    filepath = os.path.join(history_dir, filename)
    
    # Check if file exists and append if it does
    if os.path.exists(filepath):
        # Read existing history
        existing_history = pd.read_csv(filepath)
        
        # Append new requests
        combined_history = pd.concat([existing_history, requests], ignore_index=True)
        
        # Remove duplicates based on slug, meeting_days, start_date, end_date, and start_time
        combined_history = combined_history.drop_duplicates(
            subset=['slug', 'meeting_days', 'start_date', 'end_date', 'start_time'],
            keep='last'
        )
        
        # Save combined history
        combined_history.to_csv(filepath, index=False)
    else:
        # Save new history file
        requests.to_csv(filepath, index=False)
    
    return filepath

def format_meeting_days(days_str: str) -> str:
    """
    Format meeting days string for the output CSV.
    
    Args:
        days_str: Comma-separated list of meeting days (e.g., "Monday,Wednesday,Friday")
        
    Returns:
        Formatted meeting days string (e.g., "mon|wed|fri")
    """
    day_map = {
        'Monday': 'mon',
        'Tuesday': 'tue',
        'Wednesday': 'wed',
        'Thursday': 'thu',
        'Friday': 'fri',
        'Saturday': 'sat',
        'Sunday': 'sun'
    }
    
    # Split by comma and handle potential spaces
    days = [day.strip() for day in days_str.split(',')]
    
    # Map each day to its 3-letter abbreviation
    formatted_days = []
    for day in days:
        if day in day_map:
            formatted_days.append(day_map[day])
        else:
            # Try to handle already abbreviated days
            day_lower = day.lower()
            if day_lower in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']:
                formatted_days.append(day_lower)
            else:
                # Fallback - use first 3 letters
                formatted_days.append(day_lower[:3])
    
    # Join with pipe character
    return '|'.join(formatted_days) 
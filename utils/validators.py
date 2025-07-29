import re
from typing import List
import datetime
import pandas as pd
import os

def validate_slug(slug, pattern=None):
    """
    Validate that a slug matches the expected pattern.
    
    Args:
        slug: The slug to validate
        pattern: Regex pattern to match against (optional)
        
    Returns:
        True if valid, False otherwise
    """
    if not slug:
        return False
    
    # If no pattern provided or we want to be more flexible
    if pattern is None:
        # Basic validation: must start with a brand code followed by subject and grade
        # More flexible pattern that accepts most variations
        basic_pattern = r'^[a-zA-Z]+-[a-zA-Z0-9-]+'
        return bool(re.match(basic_pattern, slug))
    
    # Use the provided pattern for strict validation
    return bool(re.match(pattern, slug))

def validate_days(days):
    """
    Validate that at least one meeting day is selected.
    
    Args:
        days: List of selected meeting days
        
    Returns:
        True if valid, False otherwise
    """
    return len(days) > 0

def validate_dates(start_date, end_date):
    """
    Validate that start date is before end date.
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        True if valid, False otherwise
    """
    return start_date <= end_date

def validate_time(time):
    """
    Validate that time is valid.
    
    Args:
        time: Time to validate
        
    Returns:
        True if valid, False otherwise
    """
    return isinstance(time, datetime.time) 
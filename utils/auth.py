def check_user_role(username: str, password: str, users_config: dict) -> str:
    """
    Check user credentials and return their role.
    
    Args:
        username: Username
        password: Password
        users_config: Dictionary containing user configuration
        
    Returns:
        str: 'approver', 'requester', or None if authentication fails
    """
    if username in users_config and users_config[username]['password'] == password:
        return users_config[username]['role']
    return None 
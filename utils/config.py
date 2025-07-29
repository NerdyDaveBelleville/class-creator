import json
import os

def load_config(config_path=None):
    """
    Load configuration from the specified JSON file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Dictionary containing configuration
    """
    if config_path is None:
        # Default to the config file in the project directory
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    return config

# Load configuration once at module import
CONFIG = {
    'app': {
        'title': 'Class Creator',
        'icon': '📚',
        'layout': 'wide'
    },
    'paths': {
        'data_dir': 'data',
        'export_dir': 'exports',
        'history_dir': 'history'  # New directory for history files
    },
    'slug_format': {
        'pattern': r'^[a-zA-Z]+-[a-zA-Z0-9-]+$',
        'example': 'vtp-math-grade-6'
    },
    'users': {
        'admin': {
            'password': 'admin123',
            'role': 'admin'
        },
        'user': {
            'password': 'b3N3rdY!',
            'role': 'requester'
        }
    },
    'defaults': {
        'default_duration_minutes': 60
    }
} 
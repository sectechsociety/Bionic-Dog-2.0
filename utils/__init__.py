"""
Utility package for Bionic Dog project
"""

try:
    from .helpers import *
    
    __all__ = [
        'setup_logging',
        'send_dog_command', 
        'send_command_to_both_dogs',
        'validate_dog_connection',
        'validate_all_connections',
        'retry_with_backoff',
        'Timer'
    ]
except ImportError as e:
    print(f"Warning: Some utility functions may not be available: {e}")
    __all__ = []

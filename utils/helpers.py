"""
Utility functions for Bionic Dog project
"""

import logging
import time
from typing import Dict, List, Optional, Tuple

# Handle potential import errors gracefully
try:
    import requests
except ImportError:
    print("Warning: requests not installed. Install with: pip install requests")
    requests = None

try:
    from config.settings import DOG_URLS, COMMUNICATION
except ImportError:
    print("Warning: config.settings not found, using defaults")
    DOG_URLS = {
        'tom': "http://192.168.30.42/control",
        'jerry': "http://192.168.30.153/control"
    }
    COMMUNICATION = {'max_retry_attempts': 3}

logger = logging.getLogger(__name__)

def setup_logging(level: str = 'INFO', log_file: str = None):
    """Setup logging configuration"""
    log_level = getattr(logging, level.upper())
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    # Setup file handler if specified
    handlers = [console_handler]
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        handlers=handlers,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def send_dog_command(dog_name: str, action: str, **kwargs) -> bool:
    """Send command to a specific dog"""
    if not requests:
        logger.error("Requests module not available")
        return False
        
    try:
        base_url = DOG_URLS.get(dog_name.lower())
        if not base_url:
            logger.error(f"Unknown dog: {dog_name}")
            return False
        
        # Map actions to URL parameters
        url_params = _get_action_params(action)
        if not url_params:
            logger.error(f"Unknown action: {action}")
            return False
        
        # Handle special cases (like stop which needs multiple URLs)
        if isinstance(url_params, list):
            results = []
            for params in url_params:
                url = f"{base_url}?{params}"
                response = requests.get(url, timeout=5)
                results.append(response.status_code == 200)
            return all(results)
        else:
            url = f"{base_url}?{url_params}"
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        
    except Exception as e:
        logger.error(f"Failed to send command to {dog_name}: {str(e)}")
        return False

def _get_action_params(action: str) -> Optional[str]:
    """Map action names to URL parameters"""
    action_map = {
        # Movement
        'forward': 'var=move&val=1&cmd=0',
        'reverse': 'var=move&val=5&cmd=0',
        'left': 'var=move&val=2&cmd=0',
        'right': 'var=move&val=4&cmd=0',
        'stop': ['var=move&val=3&cmd=0', 'var=move&val=6&cmd=0'],
        'stop_fr': 'var=move&val=3&cmd=0',
        'stop_lr': 'var=move&val=6&cmd=0',
        
        # Actions
        'handshake': 'var=funcMode&val=3&cmd=0',
        'middlepos': 'var=funcMode&val=9&cmd=0',
        'initpos': 'var=funcMode&val=8&cmd=0',
        'hiphop': 'var=funcMode&val=7&cmd=0',
        'ssdance': 'var=funcMode&val=6&cmd=0',
        'bow': 'var=funcMode&val=5&cmd=0',
        'staylow': 'var=funcMode&val=2&cmd=0',
        'jump': 'var=funcMode&val=4&cmd=0',
        'steady': 'var=funcMode&val=1&cmd=0',
    }
    
    return action_map.get(action.lower())

def send_command_to_both_dogs(action: str) -> Tuple[bool, bool]:
    """Send the same command to both Tom and Jerry"""
    tom_success = send_dog_command('tom', action)
    jerry_success = send_dog_command('jerry', action)
    return tom_success, jerry_success

def validate_dog_connection(dog_name: str) -> bool:
    """Test connection to a specific dog"""
    if not requests:
        logger.warning("Requests module not available")
        return False
        
    try:
        base_url = DOG_URLS.get(dog_name.lower())
        if not base_url:
            return False
        
        # Send a simple status command
        response = requests.get(base_url, timeout=3)
        return response.status_code == 200
        
    except Exception as e:
        logger.warning(f"Connection test failed for {dog_name}: {str(e)}")
        return False

def validate_all_connections() -> Dict[str, bool]:
    """Test connections to all configured dogs"""
    results = {}
    for dog_name in DOG_URLS.keys():
        results[dog_name] = validate_dog_connection(dog_name)
    return results

def retry_with_backoff(func, max_retries: int = 3, backoff_factor: float = 1.0):
    """Retry a function with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            
            wait_time = backoff_factor * (2 ** attempt)
            logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {str(e)}")
            time.sleep(wait_time)

def format_timestamp(timestamp: float = None) -> str:
    """Format timestamp for logging"""
    if timestamp is None:
        timestamp = time.time()
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))

def calculate_distance_2d(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
    """Calculate Euclidean distance between two points"""
    return ((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)**0.5

def normalize_angle(angle: float) -> float:
    """Normalize angle to [-180, 180] degrees"""
    while angle > 180:
        angle -= 360
    while angle < -180:
        angle += 360
    return angle

def clamp_value(value: float, min_val: float, max_val: float) -> float:
    """Clamp value between min and max"""
    return max(min_val, min(max_val, value))

def create_message_id() -> str:
    """Create unique message ID"""
    return f"msg_{int(time.time() * 1000000)}"

def validate_hsv_color(hsv_tuple: Tuple[int, int, int]) -> bool:
    """Validate HSV color values"""
    h, s, v = hsv_tuple
    return (0 <= h <= 179) and (0 <= s <= 255) and (0 <= v <= 255)

def convert_bgr_to_hsv_range(bgr_color: Tuple[int, int, int], tolerance: int = 20) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
    """Convert BGR color to HSV range for color detection"""
    try:
        import cv2
        import numpy as np
        
        # Convert BGR to HSV
        bgr_array = np.uint8([[bgr_color]])
        hsv_array = cv2.cvtColor(bgr_array, cv2.COLOR_BGR2HSV)
        h, s, v = hsv_array[0][0]
        
        # Create range with tolerance
        lower_hsv = (max(0, h - tolerance), max(0, s - 50), max(0, v - 50))
        upper_hsv = (min(179, h + tolerance), 255, 255)
        
        return lower_hsv, upper_hsv
    except ImportError:
        logger.warning("OpenCV not available for color conversion")
        # Return default color ranges for red
        return (0, 50, 50), (179, 255, 255)

def get_system_info() -> Dict:
    """Get basic system information"""
    import platform
    
    try:
        import psutil
        return {
            'platform': platform.system(),
            'python_version': platform.python_version(),
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total,
            'memory_available': psutil.virtual_memory().available,
        }
    except ImportError:
        logger.warning("psutil not available for system info")
        return {
            'platform': platform.system(),
            'python_version': platform.python_version(),
        }
    except Exception as e:
        logger.error(f"Failed to get system info: {str(e)}")
        return {}

class Timer:
    """Simple timer utility"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def start(self):
        """Start the timer"""
        self.start_time = time.time()
        self.end_time = None
    
    def stop(self):
        """Stop the timer"""
        if self.start_time is None:
            logger.warning("Timer not started")
            return 0
        
        self.end_time = time.time()
        return self.elapsed()
    
    def elapsed(self) -> float:
        """Get elapsed time"""
        if self.start_time is None:
            return 0
        
        end = self.end_time if self.end_time else time.time()
        return end - self.start_time
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

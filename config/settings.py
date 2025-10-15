"""
Configuration settings for Bionic Dog features
"""

# Dog connection settings
DOG_URLS = {
    'tom': "http://192.168.30.42/control",
    'jerry': "http://192.168.30.153/control"
}

# Camera settings
CAMERA_SETTINGS = {
    'tom_camera_url': "http://10.243.146.17:5000/video_feed",
    'jerry_camera_url': None,  # Add when available
    'default_resolution': (640, 480),
    'fps': 30
}

# Voice control settings
VOICE_CONTROL = {
    'language': 'en-US',
    'energy_threshold': 300,
    'pause_threshold': 0.8,
    'recognition_timeout': 3
}

# Object detection settings
OBJECT_DETECTION = {
    'detection_methods': ['color_tracking', 'face_detection', 'template_matching'],
    'default_method': 'face_detection',
    'frame_skip': 1,  # Process every nth frame
    'min_object_area': 500
}

# Tracking settings
TRACKING_CONTROL = {
    'center_threshold': 0.15,
    'distance_threshold': 0.3,
    'max_distance': 0.8,
    'command_interval': 0.5,
    'pid_kp': 1.0,
    'pid_ki': 0.1,
    'pid_kd': 0.05
}

# Communication settings
COMMUNICATION = {
    'message_queue_size': 100,
    'heartbeat_interval': 5,  # seconds
    'sync_tolerance_ms': 50,
    'max_retry_attempts': 3
}

# Feature flags
FEATURES = {
    'voice_control_enabled': True,
    'object_following_enabled': True,
    'dog_communication_enabled': True,
    'web_interface_enabled': True,
    'logging_enabled': True
}

# Logging configuration
LOGGING = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file_logging': True,
    'log_directory': 'logs'
}

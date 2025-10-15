"""
Enhanced Bionic Dog Features Package
Contains voice control, object following, and dog-to-dog communication modules
"""

# Version information
__version__ = "2.0.0"
__author__ = "Bionic Dog Development Team"
__description__ = "Advanced AI features for bionic dog control"

# Feature availability flags (will be set based on dependencies)
FEATURES_AVAILABLE = {
    'voice_control': False,
    'object_following': False, 
    'communication': True  # Always available
}

# Try to import and initialize features
try:
    from .voice_control import VoiceController
    FEATURES_AVAILABLE['voice_control'] = True
except ImportError:
    print("Voice control features not available - missing dependencies")
    
try:
    from .object_following import FollowingBehavior
    FEATURES_AVAILABLE['object_following'] = True
except ImportError:
    print("Object following features not available - missing dependencies")
    
try:
    from .communication import MessageHandler
    FEATURES_AVAILABLE['communication'] = True
except ImportError:
    print("Communication features not available")

# Export what's available
__all__ = []

if FEATURES_AVAILABLE['voice_control']:
    __all__.append('VoiceController')
    
if FEATURES_AVAILABLE['object_following']:
    __all__.append('FollowingBehavior')
    
if FEATURES_AVAILABLE['communication']:
    __all__.append('MessageHandler')

def get_available_features():
    """Get list of available features"""
    return [feature for feature, available in FEATURES_AVAILABLE.items() if available]

def get_feature_status():
    """Get detailed feature availability status"""
    return FEATURES_AVAILABLE.copy()

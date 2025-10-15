"""
Object Following Module
Enables bionic dogs to track and follow objects using computer vision
"""

from .object_detector import ObjectDetector
from .tracking_controller import TrackingController
from .following_behavior import FollowingBehavior

__all__ = ['ObjectDetector', 'TrackingController', 'FollowingBehavior']

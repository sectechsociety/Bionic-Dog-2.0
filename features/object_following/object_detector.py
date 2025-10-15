"""
Object Detection Engine
Detects and tracks objects in camera feed for following behavior
"""

import cv2
import numpy as np
import threading
import time
from typing import Dict, List, Tuple, Optional, Callable
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class DetectionMethod(Enum):
    """Object detection methods"""
    COLOR_TRACKING = "color_tracking"
    FACE_DETECTION = "face_detection"
    YOLO_OBJECT = "yolo_object"
    TEMPLATE_MATCHING = "template_matching"

class ObjectDetector:
    """Object detection and tracking engine"""
    
    def __init__(self, camera_url: str = "http://10.243.146.17:5000/video_feed"):
        self.camera_url = camera_url
        self.detection_method = DetectionMethod.COLOR_TRACKING
        self.is_detecting = False
        self.detection_thread = None
        
        # Camera properties
        self.frame = None
        self.frame_width = 640
        self.frame_height = 480
        
        # Detection parameters
        self.target_color = None  # HSV color range for color tracking
        self.face_cascade = None  # Face detection cascade
        self.template = None  # Template for template matching
        
        # Tracking data
        self.tracked_objects = []
        self.tracking_history = []
        
        # Callbacks
        self.on_object_detected = None
        self.on_object_lost = None
        self.on_tracking_update = None
        
        # Initialize detection components
        self._initialize_detectors()
    
    def _initialize_detectors(self):
        """Initialize detection algorithms"""
        try:
            # Load face detection cascade
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            logger.info("Face detection initialized")
            
        except Exception as e:
            logger.error(f"Error initializing detectors: {str(e)}")
    
    def start_detection(self, method: DetectionMethod = DetectionMethod.COLOR_TRACKING):
        """Start object detection"""
        if self.is_detecting:
            logger.warning("Detection already running")
            return False
        
        self.detection_method = method
        self.is_detecting = True
        
        # Start detection thread
        self.detection_thread = threading.Thread(target=self._detection_loop)
        self.detection_thread.daemon = True
        self.detection_thread.start()
        
        logger.info(f"Object detection started with method: {method.value}")
        return True
    
    def stop_detection(self):
        """Stop object detection"""
        self.is_detecting = False
        
        if self.detection_thread and self.detection_thread.is_alive():
            self.detection_thread.join(timeout=2)
        
        logger.info("Object detection stopped")
    
    def _detection_loop(self):
        """Main detection loop"""
        cap = None
        
        try:
            # Try to connect to camera
            cap = cv2.VideoCapture(self.camera_url)
            
            if not cap.isOpened():
                logger.error(f"Failed to open camera: {self.camera_url}")
                return
            
            logger.info("Camera connected successfully")
            
            while self.is_detecting:
                ret, frame = cap.read()
                
                if not ret:
                    logger.warning("Failed to read frame from camera")
                    time.sleep(0.1)
                    continue
                
                self.frame = frame
                self.frame_height, self.frame_width = frame.shape[:2]
                
                # Perform detection based on selected method
                detected_objects = self._detect_objects(frame)
                
                # Update tracking
                self._update_tracking(detected_objects)
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.033)  # ~30 FPS
                
        except Exception as e:
            logger.error(f"Error in detection loop: {str(e)}")
        finally:
            if cap:
                cap.release()
    
    def _detect_objects(self, frame) -> List[Dict]:
        """Detect objects based on selected method"""
        detected_objects = []
        
        try:
            if self.detection_method == DetectionMethod.COLOR_TRACKING:
                detected_objects = self._detect_by_color(frame)
            elif self.detection_method == DetectionMethod.FACE_DETECTION:
                detected_objects = self._detect_faces(frame)
            elif self.detection_method == DetectionMethod.TEMPLATE_MATCHING:
                detected_objects = self._detect_by_template(frame)
            # YOLO detection would be implemented here if needed
            
        except Exception as e:
            logger.error(f"Error in object detection: {str(e)}")
        
        return detected_objects
    
    def _detect_by_color(self, frame) -> List[Dict]:
        """Detect objects by color tracking"""
        if not self.target_color:
            return []
        
        detected_objects = []
        
        try:
            # Convert frame to HSV
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Create mask for target color
            mask = cv2.inRange(hsv, self.target_color['lower'], self.target_color['upper'])
            
            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                # Filter by area
                area = cv2.contourArea(contour)
                if area > 500:  # Minimum area threshold
                    
                    # Get bounding rectangle
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Calculate center
                    center_x = x + w // 2
                    center_y = y + h // 2
                    
                    detected_objects.append({
                        'type': 'color_object',
                        'bbox': (x, y, w, h),
                        'center': (center_x, center_y),
                        'area': area,
                        'confidence': min(area / 5000, 1.0)  # Normalized confidence
                    })
            
        except Exception as e:
            logger.error(f"Error in color detection: {str(e)}")
        
        return detected_objects
    
    def _detect_faces(self, frame) -> List[Dict]:
        """Detect faces in the frame"""
        if not self.face_cascade:
            return []
        
        detected_objects = []
        
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, w, h) in faces:
                center_x = x + w // 2
                center_y = y + h // 2
                
                detected_objects.append({
                    'type': 'face',
                    'bbox': (x, y, w, h),
                    'center': (center_x, center_y),
                    'area': w * h,
                    'confidence': 0.8  # Face detection confidence
                })
            
        except Exception as e:
            logger.error(f"Error in face detection: {str(e)}")
        
        return detected_objects
    
    def _detect_by_template(self, frame) -> List[Dict]:
        """Detect objects using template matching"""
        if self.template is None:
            return []
        
        detected_objects = []
        
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            template_gray = cv2.cvtColor(self.template, cv2.COLOR_BGR2GRAY)
            
            # Perform template matching
            result = cv2.matchTemplate(gray, template_gray, cv2.TM_CCOEFF_NORMED)
            
            # Find locations with high correlation
            threshold = 0.7
            locations = np.where(result >= threshold)
            
            template_h, template_w = template_gray.shape
            
            for pt in zip(*locations[::-1]):
                x, y = pt
                center_x = x + template_w // 2
                center_y = y + template_h // 2
                
                detected_objects.append({
                    'type': 'template_match',
                    'bbox': (x, y, template_w, template_h),
                    'center': (center_x, center_y),
                    'area': template_w * template_h,
                    'confidence': result[y, x]
                })
            
        except Exception as e:
            logger.error(f"Error in template matching: {str(e)}")
        
        return detected_objects
    
    def _update_tracking(self, detected_objects: List[Dict]):
        """Update object tracking information"""
        # Store current objects
        self.tracked_objects = detected_objects
        
        # Add to history
        timestamp = time.time()
        self.tracking_history.append({
            'timestamp': timestamp,
            'objects': detected_objects
        })
        
        # Keep only recent history (last 30 entries)
        if len(self.tracking_history) > 30:
            self.tracking_history = self.tracking_history[-30:]
        
        # Trigger callbacks
        if detected_objects:
            if self.on_object_detected:
                self.on_object_detected(detected_objects)
            if self.on_tracking_update:
                self.on_tracking_update(detected_objects)
        else:
            if self.on_object_lost:
                self.on_object_lost()
    
    def set_color_target(self, lower_hsv: Tuple[int, int, int], upper_hsv: Tuple[int, int, int]):
        """Set target color range for color tracking"""
        self.target_color = {
            'lower': np.array(lower_hsv),
            'upper': np.array(upper_hsv)
        }
        logger.info(f"Color target set: {lower_hsv} to {upper_hsv}")
    
    def set_template(self, template_image: np.ndarray):
        """Set template image for template matching"""
        self.template = template_image
        logger.info("Template image set for tracking")
    
    def get_current_frame(self) -> Optional[np.ndarray]:
        """Get the current camera frame"""
        return self.frame
    
    def get_tracked_objects(self) -> List[Dict]:
        """Get currently tracked objects"""
        return self.tracked_objects
    
    def get_primary_target(self) -> Optional[Dict]:
        """Get the primary target (largest/closest object)"""
        if not self.tracked_objects:
            return None
        
        # Return the object with highest confidence or largest area
        return max(self.tracked_objects, key=lambda obj: obj.get('confidence', 0) * obj.get('area', 0))
    
    def calculate_object_position(self, obj: Dict) -> Dict:
        """Calculate relative position of object in frame"""
        if not obj or 'center' not in obj:
            return {}
        
        center_x, center_y = obj['center']
        frame_center_x = self.frame_width // 2
        frame_center_y = self.frame_height // 2
        
        # Calculate relative position (-1 to 1)
        rel_x = (center_x - frame_center_x) / frame_center_x
        rel_y = (center_y - frame_center_y) / frame_center_y
        
        # Calculate distance from center
        distance = np.sqrt(rel_x**2 + rel_y**2)
        
        return {
            'relative_x': rel_x,
            'relative_y': rel_y,
            'distance_from_center': distance,
            'frame_position': 'center' if distance < 0.2 else 'off_center'
        }

"""
Following Behavior Manager
High-level coordination of object following behaviors
"""

import time
import logging
from typing import Dict, Optional, Callable
from .object_detector import ObjectDetector, DetectionMethod
from .tracking_controller import TrackingController, TrackingMode

logger = logging.getLogger(__name__)

class FollowingBehavior:
    """High-level manager for object following behaviors"""
    
    def __init__(self, dog_control_callback: Callable[[str, str], bool] = None):
        self.object_detector = ObjectDetector()
        self.tracking_controller = TrackingController(dog_control_callback)
        
        self.is_active = False
        self.current_mode = TrackingMode.FOLLOW
        self.target_selection_mode = 'automatic'  # 'automatic' or 'manual'
        self.selected_target_type = 'face'  # 'face', 'color', 'template'
        
        # Following statistics
        self.stats = {
            'session_start_time': None,
            'total_detections': 0,
            'successful_follows': 0,
            'lost_target_count': 0
        }
        
        # Setup callbacks
        self.object_detector.on_object_detected = self._on_object_detected
        self.object_detector.on_object_lost = self._on_object_lost
        self.object_detector.on_tracking_update = self._on_tracking_update
    
    def start_following(self, target_dog: str = 'tom', 
                       detection_method: DetectionMethod = DetectionMethod.FACE_DETECTION,
                       tracking_mode: TrackingMode = TrackingMode.FOLLOW) -> bool:
        """Start object following behavior"""
        try:
            if self.is_active:
                logger.warning("Following behavior already active")
                return False
            
            # Start detection
            if not self.object_detector.start_detection(detection_method):
                logger.error("Failed to start object detection")
                return False
            
            # Start tracking
            if not self.tracking_controller.start_tracking(target_dog, tracking_mode):
                logger.error("Failed to start tracking controller")
                self.object_detector.stop_detection()
                return False
            
            self.is_active = True
            self.current_mode = tracking_mode
            
            # Initialize statistics
            self.stats['session_start_time'] = time.time()
            self.stats['total_detections'] = 0
            self.stats['successful_follows'] = 0
            self.stats['lost_target_count'] = 0
            
            logger.info(f"Following behavior started for {target_dog} using {detection_method.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start following behavior: {str(e)}")
            return False
    
    def stop_following(self):
        """Stop object following behavior"""
        try:
            if not self.is_active:
                logger.warning("Following behavior not active")
                return
            
            # Stop components
            self.tracking_controller.stop_tracking()
            self.object_detector.stop_detection()
            
            self.is_active = False
            
            # Log session statistics
            self._log_session_stats()
            
            logger.info("Following behavior stopped")
            
        except Exception as e:
            logger.error(f"Error stopping following behavior: {str(e)}")
    
    def _on_object_detected(self, detected_objects):
        """Handle object detection event"""
        self.stats['total_detections'] += 1
        
        # Select target based on criteria
        target = self._select_target(detected_objects)
        
        if target:
            self.tracking_controller.update_target(target)
            logger.debug(f"Target selected: {target['type']} at {target['center']}")
    
    def _on_object_lost(self):
        """Handle object lost event"""
        self.stats['lost_target_count'] += 1
        self.tracking_controller.update_target(None)
        logger.debug("Target lost")
    
    def _on_tracking_update(self, detected_objects):
        """Handle tracking update event"""
        if detected_objects:
            # Update target selection
            target = self._select_target(detected_objects)
            self.tracking_controller.update_target(target)
    
    def _select_target(self, detected_objects) -> Optional[Dict]:
        """Select the best target from detected objects"""
        if not detected_objects:
            return None
        
        if self.target_selection_mode == 'automatic':
            return self._auto_select_target(detected_objects)
        else:
            return self._manual_select_target(detected_objects)
    
    def _auto_select_target(self, detected_objects) -> Optional[Dict]:
        """Automatically select the best target"""
        # Filter by preferred type if specified
        if self.selected_target_type != 'any':
            filtered_objects = [obj for obj in detected_objects 
                              if obj.get('type') == self.selected_target_type]
            if filtered_objects:
                detected_objects = filtered_objects
        
        # Select based on priority: confidence > area > distance from center
        best_target = None
        best_score = 0
        
        for obj in detected_objects:
            # Calculate selection score
            confidence = obj.get('confidence', 0.5)
            area = obj.get('area', 0)
            center_x, center_y = obj.get('center', (0, 0))
            
            # Distance from frame center (normalized)
            frame_width = self.object_detector.frame_width or 640
            frame_height = self.object_detector.frame_height or 480
            
            center_distance = ((center_x - frame_width//2)**2 + 
                             (center_y - frame_height//2)**2)**0.5
            max_distance = (frame_width**2 + frame_height**2)**0.5
            normalized_center_distance = center_distance / max_distance
            
            # Combined score (higher is better)
            score = (confidence * 0.4 + 
                    min(area / 10000, 1.0) * 0.4 + 
                    (1 - normalized_center_distance) * 0.2)
            
            if score > best_score:
                best_score = score
                best_target = obj
        
        return best_target
    
    def _manual_select_target(self, detected_objects) -> Optional[Dict]:
        """Manual target selection (placeholder for UI integration)"""
        # For now, return the first object matching the selected type
        for obj in detected_objects:
            if obj.get('type') == self.selected_target_type:
                return obj
        
        # Fallback to first object if no type match
        return detected_objects[0] if detected_objects else None
    
    def set_color_target(self, lower_hsv, upper_hsv):
        """Set color range for color-based following"""
        self.object_detector.set_color_target(lower_hsv, upper_hsv)
        self.selected_target_type = 'color_object'
        logger.info("Color target set for following")
    
    def set_template_target(self, template_image):
        """Set template image for template-based following"""
        self.object_detector.set_template(template_image)
        self.selected_target_type = 'template_match'
        logger.info("Template target set for following")
    
    def switch_tracking_mode(self, new_mode: TrackingMode):
        """Switch tracking mode during active following"""
        if self.is_active:
            self.current_mode = new_mode
            self.tracking_controller.tracking_mode = new_mode
            logger.info(f"Switched to tracking mode: {new_mode.value}")
    
    def set_target_selection_mode(self, mode: str, target_type: str = None):
        """Set target selection parameters"""
        self.target_selection_mode = mode
        if target_type:
            self.selected_target_type = target_type
        logger.info(f"Target selection mode: {mode}, type: {self.selected_target_type}")
    
    def get_current_status(self) -> Dict:
        """Get current following status"""
        detector_status = {
            'is_detecting': self.object_detector.is_detecting,
            'detection_method': self.object_detector.detection_method.value,
            'tracked_objects_count': len(self.object_detector.get_tracked_objects())
        }
        
        tracking_status = self.tracking_controller.get_tracking_status()
        
        return {
            'is_active': self.is_active,
            'current_mode': self.current_mode.value,
            'target_selection_mode': self.target_selection_mode,
            'selected_target_type': self.selected_target_type,
            'detector': detector_status,
            'tracking': tracking_status,
            'statistics': self.stats
        }
    
    def get_detected_objects(self):
        """Get currently detected objects"""
        return self.object_detector.get_tracked_objects()
    
    def get_current_frame(self):
        """Get current camera frame for display"""
        return self.object_detector.get_current_frame()
    
    def configure_tracking_parameters(self, **kwargs):
        """Configure tracking parameters"""
        self.tracking_controller.set_tracking_parameters(**kwargs)
    
    def _log_session_stats(self):
        """Log session statistics"""
        if self.stats['session_start_time']:
            session_duration = time.time() - self.stats['session_start_time']
            logger.info(f"Following session ended:")
            logger.info(f"  Duration: {session_duration:.2f} seconds")
            logger.info(f"  Total detections: {self.stats['total_detections']}")
            logger.info(f"  Lost target events: {self.stats['lost_target_count']}")
            
            if session_duration > 0:
                detection_rate = self.stats['total_detections'] / session_duration
                logger.info(f"  Detection rate: {detection_rate:.2f} per second")
    
    def emergency_stop(self):
        """Emergency stop for following behavior"""
        logger.warning("Emergency stop triggered for following behavior")
        try:
            self.tracking_controller.stop_tracking()
            self.object_detector.stop_detection()
            self.is_active = False
        except Exception as e:
            logger.error(f"Error during emergency stop: {str(e)}")
        
        logger.info("Following behavior emergency stopped")

"""
Tracking Controller
Controls dog movement based on object tracking data
"""

import time
import threading
from typing import Dict, Optional, Callable
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class TrackingMode(Enum):
    """Tracking behavior modes"""
    FOLLOW = "follow"
    OBSERVE = "observe"
    APPROACH = "approach"
    MAINTAIN_DISTANCE = "maintain_distance"

class TrackingController:
    """Controls dog movement based on tracking information"""
    
    def __init__(self, dog_control_callback: Callable[[str, str], bool] = None):
        self.dog_control_callback = dog_control_callback
        self.is_tracking = False
        self.tracking_thread = None
        
        # Tracking parameters
        self.target_object = None
        self.tracking_mode = TrackingMode.FOLLOW
        self.target_dog = 'tom'  # Default to Tom
        
        # Control parameters
        self.center_threshold = 0.15  # Tolerance for "centered" position
        self.distance_threshold = 0.3  # Minimum distance to maintain
        self.max_distance = 0.8  # Maximum distance before moving closer
        
        # Movement timing
        self.last_command_time = 0
        self.command_interval = 0.5  # Minimum time between commands (seconds)
        
        # PID controller parameters for smooth following
        self.pid_kp = 1.0  # Proportional gain
        self.pid_ki = 0.1  # Integral gain
        self.pid_kd = 0.05  # Derivative gain
        self.pid_error_sum = 0
        self.pid_last_error = 0
    
    def start_tracking(self, target_dog: str = 'tom', mode: TrackingMode = TrackingMode.FOLLOW) -> bool:
        """Start tracking mode"""
        if self.is_tracking:
            logger.warning("Tracking already active")
            return False
        
        self.target_dog = target_dog
        self.tracking_mode = mode
        self.is_tracking = True
        
        # Reset PID controller
        self.pid_error_sum = 0
        self.pid_last_error = 0
        
        # Start tracking thread
        self.tracking_thread = threading.Thread(target=self._tracking_loop)
        self.tracking_thread.daemon = True
        self.tracking_thread.start()
        
        logger.info(f"Started tracking mode for {target_dog} with mode: {mode.value}")
        return True
    
    def stop_tracking(self):
        """Stop tracking mode"""
        self.is_tracking = False
        
        if self.tracking_thread and self.tracking_thread.is_alive():
            self.tracking_thread.join(timeout=2)
        
        # Send stop command to dog
        self._send_command('stop')
        
        logger.info("Stopped tracking mode")
    
    def update_target(self, target_object: Optional[Dict]):
        """Update the target object being tracked"""
        self.target_object = target_object
    
    def _tracking_loop(self):
        """Main tracking control loop"""
        while self.is_tracking:
            try:
                if self.target_object:
                    self._process_tracking_update()
                else:
                    # No target - search behavior
                    self._search_for_target()
                
                # Sleep to prevent excessive CPU usage
                time.sleep(0.1)  # 10Hz update rate
                
            except Exception as e:
                logger.error(f"Error in tracking loop: {str(e)}")
                time.sleep(0.5)
    
    def _process_tracking_update(self):
        """Process target object and determine movement"""
        if not self.target_object:
            return
        
        # Calculate object position
        obj_position = self._calculate_position_metrics(self.target_object)
        
        if self.tracking_mode == TrackingMode.FOLLOW:
            self._execute_follow_behavior(obj_position)
        elif self.tracking_mode == TrackingMode.OBSERVE:
            self._execute_observe_behavior(obj_position)
        elif self.tracking_mode == TrackingMode.APPROACH:
            self._execute_approach_behavior(obj_position)
        elif self.tracking_mode == TrackingMode.MAINTAIN_DISTANCE:
            self._execute_maintain_distance_behavior(obj_position)
    
    def _calculate_position_metrics(self, target_object: Dict) -> Dict:
        """Calculate position metrics from target object"""
        if 'center' not in target_object:
            return {}
        
        # Assuming frame dimensions (would come from object detector)
        frame_width = 640
        frame_height = 480
        
        center_x, center_y = target_object['center']
        
        # Calculate relative position (-1 to 1)
        rel_x = (center_x - frame_width // 2) / (frame_width // 2)
        rel_y = (center_y - frame_height // 2) / (frame_height // 2)
        
        # Calculate distance estimate based on object size
        area = target_object.get('area', 0)
        distance_estimate = 1.0 - min(area / (frame_width * frame_height * 0.3), 1.0)
        
        return {
            'relative_x': rel_x,
            'relative_y': rel_y,
            'distance_estimate': distance_estimate,
            'area': area,
            'is_centered_x': abs(rel_x) < self.center_threshold,
            'is_centered_y': abs(rel_y) < self.center_threshold,
            'is_close': distance_estimate < self.distance_threshold,
            'is_far': distance_estimate > self.max_distance
        }
    
    def _execute_follow_behavior(self, pos_metrics: Dict):
        """Execute following behavior"""
        if not pos_metrics:
            return
        
        # Determine movement based on object position
        if pos_metrics['is_far']:
            # Object is far - move forward
            self._send_command_with_timing('forward')
        elif pos_metrics['is_close']:
            # Object is too close - move backward or stop
            self._send_command_with_timing('reverse')
        else:
            # Object at good distance - adjust orientation
            if not pos_metrics['is_centered_x']:
                if pos_metrics['relative_x'] > self.center_threshold:
                    self._send_command_with_timing('right')
                elif pos_metrics['relative_x'] < -self.center_threshold:
                    self._send_command_with_timing('left')
            else:
                # Well positioned - maintain
                self._send_command_with_timing('steady')
    
    def _execute_observe_behavior(self, pos_metrics: Dict):
        """Execute observation behavior (track but don't move forward/backward)"""
        if not pos_metrics:
            return
        
        # Only adjust orientation, don't move forward/backward
        if not pos_metrics['is_centered_x']:
            if pos_metrics['relative_x'] > self.center_threshold:
                self._send_command_with_timing('right')
            elif pos_metrics['relative_x'] < -self.center_threshold:
                self._send_command_with_timing('left')
        else:
            self._send_command_with_timing('steady')
    
    def _execute_approach_behavior(self, pos_metrics: Dict):
        """Execute approach behavior (move towards object)"""
        if not pos_metrics:
            return
        
        if not pos_metrics['is_close']:
            # Not close enough - move forward and adjust orientation
            if not pos_metrics['is_centered_x']:
                # Turn towards object first
                if pos_metrics['relative_x'] > self.center_threshold:
                    self._send_command_with_timing('right')
                elif pos_metrics['relative_x'] < -self.center_threshold:
                    self._send_command_with_timing('left')
            else:
                # Centered - move forward
                self._send_command_with_timing('forward')
        else:
            # Close enough - stop and perform greeting
            self._send_command_with_timing('handshake')
    
    def _execute_maintain_distance_behavior(self, pos_metrics: Dict):
        """Execute maintain distance behavior"""
        if not pos_metrics:
            return
        
        # Use PID controller for smooth distance maintenance
        distance_error = self.distance_threshold - pos_metrics['distance_estimate']
        
        # PID calculation
        self.pid_error_sum += distance_error
        error_diff = distance_error - self.pid_last_error
        
        pid_output = (self.pid_kp * distance_error + 
                     self.pid_ki * self.pid_error_sum + 
                     self.pid_kd * error_diff)
        
        self.pid_last_error = distance_error
        
        # Convert PID output to movement commands
        if abs(pid_output) > 0.1:
            if pid_output > 0:
                self._send_command_with_timing('forward')
            else:
                self._send_command_with_timing('reverse')
        
        # Also adjust orientation
        if not pos_metrics['is_centered_x']:
            if pos_metrics['relative_x'] > self.center_threshold:
                self._send_command_with_timing('right')
            elif pos_metrics['relative_x'] < -self.center_threshold:
                self._send_command_with_timing('left')
    
    def _search_for_target(self):
        """Search behavior when no target is detected"""
        current_time = time.time()
        
        # Simple search pattern - slow rotation
        if current_time - self.last_command_time > 1.0:  # Slower search
            self._send_command('right')  # Rotate to search
            time.sleep(0.3)
            self._send_command('stop')
            self.last_command_time = current_time
    
    def _send_command_with_timing(self, command: str):
        """Send command with timing constraints"""
        current_time = time.time()
        
        if current_time - self.last_command_time >= self.command_interval:
            self._send_command(command)
            self.last_command_time = current_time
    
    def _send_command(self, command: str) -> bool:
        """Send command to the target dog"""
        if self.dog_control_callback:
            success = self.dog_control_callback(self.target_dog, command)
            if success:
                logger.debug(f"Sent command to {self.target_dog}: {command}")
            else:
                logger.warning(f"Failed to send command to {self.target_dog}: {command}")
            return success
        else:
            # Fallback logging
            logger.info(f"Tracking command for {self.target_dog}: {command}")
            return True
    
    def set_tracking_parameters(self, center_threshold: float = None, 
                              distance_threshold: float = None,
                              command_interval: float = None):
        """Update tracking parameters"""
        if center_threshold is not None:
            self.center_threshold = center_threshold
        if distance_threshold is not None:
            self.distance_threshold = distance_threshold
        if command_interval is not None:
            self.command_interval = command_interval
        
        logger.info("Tracking parameters updated")
    
    def set_pid_parameters(self, kp: float = None, ki: float = None, kd: float = None):
        """Update PID controller parameters"""
        if kp is not None:
            self.pid_kp = kp
        if ki is not None:
            self.pid_ki = ki
        if kd is not None:
            self.pid_kd = kd
        
        logger.info("PID parameters updated")
    
    def get_tracking_status(self) -> Dict:
        """Get current tracking status"""
        return {
            'is_tracking': self.is_tracking,
            'target_dog': self.target_dog,
            'tracking_mode': self.tracking_mode.value,
            'has_target': self.target_object is not None,
            'last_command_time': self.last_command_time
        }

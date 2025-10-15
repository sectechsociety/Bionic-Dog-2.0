"""
Communication Protocol for Bionic Dogs
Defines message types and communication standards
"""

from enum import Enum
from typing import Dict, Any
import json

class MessageType(Enum):
    """Predefined message types for dog communication"""
    STATUS_UPDATE = "status_update"
    SYNC_COMMAND = "sync_command"
    COORDINATE_ACTION = "coordinate_action"
    EMERGENCY_STOP = "emergency_stop"
    HEALTH_CHECK = "health_check"
    FORMATION_CONTROL = "formation_control"
    CUSTOM_ACTION = "custom_action"

class ActionType(Enum):
    """Predefined action types for coordination"""
    MOVE_FORWARD = "move_forward"
    MOVE_BACKWARD = "move_backward"
    TURN_LEFT = "turn_left"
    TURN_RIGHT = "turn_right"
    STOP = "stop"
    HANDSHAKE = "handshake"
    DANCE = "dance"
    BOW = "bow"
    JUMP = "jump"

class CommunicationProtocol:
    """Protocol handler for standardized dog communication"""
    
    @staticmethod
    def create_status_message(dog_name: str, status: str, battery: int, position: Dict = None) -> Dict:
        """Create a status update message"""
        return {
            'type': MessageType.STATUS_UPDATE.value,
            'data': {
                'dog_name': dog_name,
                'status': status,
                'battery': battery,
                'position': position or {'x': 0, 'y': 0, 'heading': 0},
                'capabilities': ['move', 'dance', 'handshake', 'jump']
            }
        }
    
    @staticmethod
    def create_sync_command(action: str, delay_ms: int = 0, duration_ms: int = 1000) -> Dict:
        """Create a synchronized action command"""
        return {
            'type': MessageType.SYNC_COMMAND.value,
            'data': {
                'action': action,
                'delay_ms': delay_ms,
                'duration_ms': duration_ms,
                'sync_timestamp': None  # Will be set by sync controller
            }
        }
    
    @staticmethod
    def create_coordinate_action(leader: str, followers: list, action: str, formation: Dict = None) -> Dict:
        """Create a coordinated action message"""
        return {
            'type': MessageType.COORDINATE_ACTION.value,
            'data': {
                'leader': leader,
                'followers': followers,
                'action': action,
                'formation': formation or {'type': 'line', 'spacing': 1.0},
                'execution_order': 'simultaneous'  # or 'sequential'
            }
        }
    
    @staticmethod
    def create_emergency_stop() -> Dict:
        """Create an emergency stop message"""
        return {
            'type': MessageType.EMERGENCY_STOP.value,
            'data': {
                'priority': 'critical',
                'immediate': True,
                'reason': 'user_initiated'
            }
        }
    
    @staticmethod
    def create_formation_control(formation_type: str, positions: Dict) -> Dict:
        """Create a formation control message"""
        return {
            'type': MessageType.FORMATION_CONTROL.value,
            'data': {
                'formation_type': formation_type,  # 'line', 'circle', 'triangle', etc.
                'positions': positions,  # {'tom': {'x': 0, 'y': 0}, 'jerry': {'x': 1, 'y': 0}}
                'transition_time': 3000,  # milliseconds
                'maintain_formation': True
            }
        }
    
    @staticmethod
    def validate_message(message: Dict) -> bool:
        """Validate if message follows the protocol"""
        required_fields = ['type', 'data']
        
        if not all(field in message for field in required_fields):
            return False
        
        # Check if message type is valid
        valid_types = [mt.value for mt in MessageType]
        if message['type'] not in valid_types:
            return False
        
        return True
    
    @staticmethod
    def serialize_message(message: Dict) -> str:
        """Serialize message to JSON string"""
        return json.dumps(message, indent=2)
    
    @staticmethod
    def deserialize_message(message_str: str) -> Dict:
        """Deserialize JSON string to message dict"""
        try:
            return json.loads(message_str)
        except json.JSONDecodeError:
            return {}

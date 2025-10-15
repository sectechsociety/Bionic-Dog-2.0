"""
Message Handler for Dog-to-Dog Communication
Handles message passing between Tom and Jerry
"""

import json
import time
from typing import Dict, List, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageHandler:
    def __init__(self):
        self.message_queue = []
        self.dog_status = {
            'tom': {'status': 'idle', 'last_seen': None, 'battery': 100},
            'jerry': {'status': 'idle', 'last_seen': None, 'battery': 100}
        }
        
    def send_message(self, from_dog: str, to_dog: str, message_type: str, data: Dict) -> bool:
        """Send a message from one dog to another"""
        try:
            message = {
                'id': int(time.time() * 1000),  # timestamp as message ID
                'from': from_dog,
                'to': to_dog,
                'type': message_type,
                'data': data,
                'timestamp': datetime.now().isoformat()
            }
            
            self.message_queue.append(message)
            logger.info(f"Message sent from {from_dog} to {to_dog}: {message_type}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")
            return False
    
    def get_messages(self, for_dog: str) -> List[Dict]:
        """Get all pending messages for a specific dog"""
        messages = [msg for msg in self.message_queue if msg['to'] == for_dog]
        # Remove retrieved messages from queue
        self.message_queue = [msg for msg in self.message_queue if msg['to'] != for_dog]
        return messages
    
    def update_dog_status(self, dog_name: str, status: str, battery: int = None):
        """Update the status of a dog"""
        if dog_name in self.dog_status:
            self.dog_status[dog_name]['status'] = status
            self.dog_status[dog_name]['last_seen'] = datetime.now().isoformat()
            if battery is not None:
                self.dog_status[dog_name]['battery'] = battery
    
    def get_dog_status(self, dog_name: str = None) -> Dict:
        """Get status of a specific dog or all dogs"""
        if dog_name:
            return self.dog_status.get(dog_name, {})
        return self.dog_status
    
    def broadcast_message(self, from_dog: str, message_type: str, data: Dict) -> bool:
        """Broadcast a message to all other dogs"""
        success = True
        for dog in self.dog_status.keys():
            if dog != from_dog:
                if not self.send_message(from_dog, dog, message_type, data):
                    success = False
        return success

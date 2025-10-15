"""
Synchronization Controller for Coordinated Actions
Ensures precise timing for synchronized movements between dogs
"""

import time
import asyncio
from typing import Dict, List, Callable
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class SyncController:
    """Controller for synchronized actions between multiple dogs"""
    
    def __init__(self, message_handler):
        self.message_handler = message_handler
        self.active_syncs = {}
        self.sync_tolerance_ms = 50  # Acceptable timing variance
        
    async def execute_synchronized_action(self, dogs: List[str], action: str, delay_ms: int = 0) -> bool:
        """Execute an action simultaneously across multiple dogs"""
        try:
            # Calculate execution timestamp
            execution_time = datetime.now() + timedelta(milliseconds=delay_ms + 1000)  # 1 second prep time
            sync_timestamp = execution_time.timestamp() * 1000
            
            # Send sync commands to all dogs
            sync_id = f"sync_{int(time.time() * 1000)}"
            
            for dog in dogs:
                sync_message = {
                    'sync_id': sync_id,
                    'action': action,
                    'execution_timestamp': sync_timestamp,
                    'participants': dogs
                }
                
                success = self.message_handler.send_message(
                    'controller', dog, 'sync_command', sync_message
                )
                
                if not success:
                    logger.error(f"Failed to send sync command to {dog}")
                    return False
            
            # Store sync info for monitoring
            self.active_syncs[sync_id] = {
                'dogs': dogs,
                'action': action,
                'execution_time': execution_time,
                'status': 'pending'
            }
            
            logger.info(f"Synchronized action '{action}' scheduled for {dogs} at {execution_time}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to execute synchronized action: {str(e)}")
            return False
    
    async def execute_formation_move(self, formation_config: Dict) -> bool:
        """Execute a formation movement with multiple dogs"""
        try:
            formation_type = formation_config.get('type', 'line')
            dogs = list(formation_config.get('positions', {}).keys())
            
            if len(dogs) < 2:
                logger.error("Formation requires at least 2 dogs")
                return False
            
            # Send formation commands
            for dog in dogs:
                position = formation_config['positions'][dog]
                formation_message = {
                    'formation_type': formation_type,
                    'target_position': position,
                    'other_dogs': [d for d in dogs if d != dog],
                    'coordination_mode': 'formation'
                }
                
                success = self.message_handler.send_message(
                    'controller', dog, 'formation_control', formation_message
                )
                
                if not success:
                    logger.error(f"Failed to send formation command to {dog}")
                    return False
            
            logger.info(f"Formation '{formation_type}' command sent to {dogs}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to execute formation move: {str(e)}")
            return False
    
    async def execute_sequential_action(self, dogs: List[str], action: str, interval_ms: int = 500) -> bool:
        """Execute an action sequentially across dogs with specified intervals"""
        try:
            for i, dog in enumerate(dogs):
                delay = i * interval_ms
                
                # Schedule individual action
                await asyncio.sleep(delay / 1000.0)
                
                action_message = {
                    'action': action,
                    'sequence_position': i,
                    'total_dogs': len(dogs)
                }
                
                success = self.message_handler.send_message(
                    'controller', dog, 'custom_action', action_message
                )
                
                if not success:
                    logger.error(f"Failed to send sequential action to {dog}")
                    return False
                
                logger.info(f"Sequential action '{action}' sent to {dog} (position {i+1}/{len(dogs)})")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to execute sequential action: {str(e)}")
            return False
    
    def get_sync_status(self, sync_id: str = None) -> Dict:
        """Get status of synchronization operations"""
        if sync_id:
            return self.active_syncs.get(sync_id, {})
        return self.active_syncs
    
    def cleanup_completed_syncs(self):
        """Remove completed synchronization records"""
        current_time = datetime.now()
        completed_syncs = []
        
        for sync_id, sync_info in self.active_syncs.items():
            if current_time > sync_info['execution_time'] + timedelta(seconds=10):
                completed_syncs.append(sync_id)
        
        for sync_id in completed_syncs:
            del self.active_syncs[sync_id]
        
        if completed_syncs:
            logger.info(f"Cleaned up {len(completed_syncs)} completed sync operations")

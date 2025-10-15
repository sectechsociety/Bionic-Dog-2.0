"""
Voice Controller
Integrates speech recognition with command processing and dog control
"""

import asyncio
import logging
from typing import Dict, Callable, Optional
from .speech_recognizer import SpeechRecognizer
from .command_processor import CommandProcessor

logger = logging.getLogger(__name__)

class VoiceController:
    """Main voice control interface for bionic dogs"""
    
    def __init__(self, dog_control_callback: Callable[[str, str], bool] = None):
        self.speech_recognizer = SpeechRecognizer()
        self.command_processor = CommandProcessor()
        self.dog_control_callback = dog_control_callback
        
        self.is_active = False
        self.voice_feedback_enabled = True
        self.command_history = []
        
        # Setup speech recognizer callbacks
        self.speech_recognizer.on_command_recognized = self._on_speech_recognized
        self.speech_recognizer.on_listening_started = self._on_listening_started
        self.speech_recognizer.on_listening_stopped = self._on_listening_stopped
    
    def start_voice_control(self) -> bool:
        """Start voice control system"""
        try:
            if self.is_active:
                logger.warning("Voice control is already active")
                return True
            
            # Test microphone first
            if not self.speech_recognizer.test_microphone():
                logger.error("Microphone test failed")
                return False
            
            self.speech_recognizer.start_listening()
            self.is_active = True
            
            logger.info("Voice control system started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start voice control: {str(e)}")
            return False
    
    def stop_voice_control(self):
        """Stop voice control system"""
        try:
            if not self.is_active:
                logger.warning("Voice control is not active")
                return
            
            self.speech_recognizer.stop_listening()
            self.is_active = False
            
            logger.info("Voice control system stopped")
            
        except Exception as e:
            logger.error(f"Error stopping voice control: {str(e)}")
    
    def _on_speech_recognized(self, text: str):
        """Handle recognized speech"""
        logger.info(f"Speech recognized: '{text}'")
        
        # Process the command
        command_result = self.command_processor.process_command(text)
        
        # Add to history
        self.command_history.append({
            'timestamp': logging.getLoggerClass().formatTime(self),
            'input': text,
            'result': command_result
        })
        
        # Keep only last 50 commands
        if len(self.command_history) > 50:
            self.command_history = self.command_history[-50:]
        
        # Execute command if recognized
        if command_result['success']:
            self._execute_command(command_result)
        else:
            logger.warning(f"Command not recognized: '{text}'")
            self._handle_unrecognized_command(text)
    
    def _execute_command(self, command_result: Dict):
        """Execute a recognized command"""
        try:
            target = command_result['target']
            action = command_result['action']
            command_type = command_result['command_type']
            
            logger.info(f"Executing command - Target: {target}, Action: {action}, Type: {command_type}")
            
            # Handle different command types
            if command_type == 'coordination':
                success = self._execute_coordination_command(action)
            else:
                # Regular dog commands
                if target == 'both' or target == 'all':
                    success_tom = self._send_dog_command('tom', action)
                    success_jerry = self._send_dog_command('jerry', action)
                    success = success_tom and success_jerry
                else:
                    success = self._send_dog_command(target, action)
            
            if success:
                logger.info(f"Command executed successfully: {action}")
            else:
                logger.error(f"Failed to execute command: {action}")
            
        except Exception as e:
            logger.error(f"Error executing command: {str(e)}")
    
    def _send_dog_command(self, dog_name: str, action: str) -> bool:
        """Send command to specific dog"""
        if self.dog_control_callback:
            return self.dog_control_callback(dog_name, action)
        else:
            # Fallback: log the command
            logger.info(f"Would send command to {dog_name}: {action}")
            return True
    
    def _execute_coordination_command(self, action: str) -> bool:
        """Execute coordination commands that involve both dogs"""
        coordination_commands = {
            'perform_handshake': self._perform_handshake,
            'disco': self._perform_disco,
            'follow_mode': self._activate_follow_mode
        }
        
        command_func = coordination_commands.get(action)
        if command_func:
            return command_func()
        else:
            logger.error(f"Unknown coordination command: {action}")
            return False
    
    def _perform_handshake(self) -> bool:
        """Execute handshake coordination"""
        try:
            # Move both dogs forward
            success1 = self._send_dog_command('tom', 'forward')
            success2 = self._send_dog_command('jerry', 'forward')
            
            if success1 and success2:
                # Wait a moment, then handshake
                asyncio.create_task(self._delayed_handshake())
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error in handshake coordination: {str(e)}")
            return False
    
    async def _delayed_handshake(self):
        """Execute handshake after delay"""
        await asyncio.sleep(1)
        self._send_dog_command('tom', 'handshake')
        self._send_dog_command('jerry', 'handshake')
        
        await asyncio.sleep(1)
        self._send_dog_command('tom', 'stop')
        self._send_dog_command('jerry', 'stop')
    
    def _perform_disco(self) -> bool:
        """Execute disco coordination"""
        try:
            # Both dogs SS Dance
            success1 = self._send_dog_command('tom', 'ssdance')
            success2 = self._send_dog_command('jerry', 'ssdance')
            
            if success1 and success2:
                # Follow with hip hop after delay
                asyncio.create_task(self._delayed_hiphop())
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error in disco coordination: {str(e)}")
            return False
    
    async def _delayed_hiphop(self):
        """Execute hip hop after delay"""
        await asyncio.sleep(1)
        self._send_dog_command('tom', 'hiphop')
        self._send_dog_command('jerry', 'hiphop')
    
    def _activate_follow_mode(self) -> bool:
        """Activate follow mode (placeholder for object following feature)"""
        logger.info("Follow mode activated - integrating with object following system")
        # This would integrate with the object following feature
        return True
    
    def _handle_unrecognized_command(self, text: str):
        """Handle unrecognized commands"""
        suggestions = self.command_processor.suggest_corrections(text)
        
        if suggestions:
            logger.info(f"Command suggestions for '{text}': {suggestions}")
        else:
            logger.info("No command suggestions available")
    
    def _on_listening_started(self):
        """Handle listening started event"""
        logger.info("Voice control listening started")
    
    def _on_listening_stopped(self):
        """Handle listening stopped event"""
        logger.info("Voice control listening stopped")
    
    def get_command_history(self, limit: int = 10) -> list:
        """Get recent command history"""
        return self.command_history[-limit:]
    
    def get_available_commands(self) -> Dict:
        """Get all available voice commands"""
        return self.command_processor.get_available_commands()
    
    def set_language(self, language: str):
        """Set speech recognition language"""
        self.speech_recognizer.set_language(language)
    
    def adjust_microphone_sensitivity(self, sensitivity: int):
        """Adjust microphone sensitivity"""
        self.speech_recognizer.adjust_sensitivity(sensitivity)
    
    def add_custom_command(self, name: str, patterns: list, action: str, command_type: str = 'action'):
        """Add a custom voice command"""
        from .command_processor import CommandType
        
        cmd_type = CommandType.ACTION
        if command_type.lower() == 'movement':
            cmd_type = CommandType.MOVEMENT
        elif command_type.lower() == 'coordination':
            cmd_type = CommandType.COORDINATION
        elif command_type.lower() == 'system':
            cmd_type = CommandType.SYSTEM
        
        self.command_processor.add_custom_command(name, patterns, cmd_type, action)
        logger.info(f"Added custom voice command: {name}")
    
    def is_voice_control_active(self) -> bool:
        """Check if voice control is currently active"""
        return self.is_active

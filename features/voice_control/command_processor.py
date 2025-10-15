"""
Command Processor for Voice Commands
Parses voice input and maps to dog actions
"""

import re
from typing import Dict, List, Optional, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class CommandType(Enum):
    """Types of voice commands"""
    MOVEMENT = "movement"
    ACTION = "action"
    COORDINATION = "coordination"
    SYSTEM = "system"
    UNKNOWN = "unknown"

class CommandProcessor:
    """Processes voice commands and maps them to dog actions"""
    
    def __init__(self):
        self.command_patterns = self._initialize_command_patterns()
        self.dog_names = ['tom', 'jerry', 'both', 'all']
        self.last_target = 'both'  # Default target if not specified
    
    def _initialize_command_patterns(self) -> Dict:
        """Initialize command patterns for recognition"""
        return {
            # Movement commands
            'forward': {
                'patterns': [r'.*\b(go forward|move forward|forward|go ahead)\b.*'],
                'type': CommandType.MOVEMENT,
                'action': 'forward'
            },
            'backward': {
                'patterns': [r'.*\b(go back|move back|backward|reverse|back up)\b.*'],
                'type': CommandType.MOVEMENT,
                'action': 'reverse'
            },
            'left': {
                'patterns': [r'.*\b(turn left|go left|left turn|left)\b.*'],
                'type': CommandType.MOVEMENT,
                'action': 'left'
            },
            'right': {
                'patterns': [r'.*\b(turn right|go right|right turn|right)\b.*'],
                'type': CommandType.MOVEMENT,
                'action': 'right'
            },
            'stop': {
                'patterns': [r'.*\b(stop|halt|freeze|pause|stay)\b.*'],
                'type': CommandType.MOVEMENT,
                'action': 'stop'
            },
            
            # Action commands
            'handshake': {
                'patterns': [r'.*\b(handshake|shake hands|greet|hello)\b.*'],
                'type': CommandType.ACTION,
                'action': 'handshake'
            },
            'dance': {
                'patterns': [r'.*\b(dance|groove|ss dance|hip hop|hiphop)\b.*'],
                'type': CommandType.ACTION,
                'action': 'ssdance'
            },
            'bow': {
                'patterns': [r'.*\b(bow|bow down|take a bow)\b.*'],
                'type': CommandType.ACTION,
                'action': 'bow'
            },
            'jump': {
                'patterns': [r'.*\b(jump|hop|leap)\b.*'],
                'type': CommandType.ACTION,
                'action': 'jump'
            },
            'sit': {
                'patterns': [r'.*\b(sit|sit down|stay low|crouch)\b.*'],
                'type': CommandType.ACTION,
                'action': 'staylow'
            },
            'stand': {
                'patterns': [r'.*\b(stand|stand up|get up|steady)\b.*'],
                'type': CommandType.ACTION,
                'action': 'steady'
            },
            
            # Coordination commands
            'perform_handshake': {
                'patterns': [r'.*\b(perform handshake|both shake|greet each other)\b.*'],
                'type': CommandType.COORDINATION,
                'action': 'perform_handshake'
            },
            'disco': {
                'patterns': [r'.*\b(disco|party time|dance together|both dance)\b.*'],
                'type': CommandType.COORDINATION,
                'action': 'disco'
            },
            'follow_me': {
                'patterns': [r'.*\b(follow me|come here|follow)\b.*'],
                'type': CommandType.COORDINATION,
                'action': 'follow_mode'
            },
            
            # System commands
            'activate': {
                'patterns': [r'.*\b(activate|wake up|start|begin)\b.*'],
                'type': CommandType.SYSTEM,
                'action': 'activate'
            },
            'deactivate': {
                'patterns': [r'.*\b(deactivate|sleep|shutdown|end)\b.*'],
                'type': CommandType.SYSTEM,
                'action': 'deactivate'
            }
        }
    
    def process_command(self, voice_input: str) -> Dict:
        """Process voice input and return command information"""
        voice_input = voice_input.lower().strip()
        logger.info(f"Processing voice command: '{voice_input}'")
        
        # Extract target (which dog)
        target = self._extract_target(voice_input)
        if not target:
            target = self.last_target
        else:
            self.last_target = target
        
        # Find matching command
        command_info = self._match_command(voice_input)
        
        if command_info:
            result = {
                'success': True,
                'target': target,
                'command_type': command_info['type'].value,
                'action': command_info['action'],
                'original_input': voice_input,
                'confidence': self._calculate_confidence(voice_input, command_info)
            }
        else:
            result = {
                'success': False,
                'target': target,
                'command_type': CommandType.UNKNOWN.value,
                'action': None,
                'original_input': voice_input,
                'error': 'Command not recognized'
            }
        
        logger.info(f"Processed command: {result}")
        return result
    
    def _extract_target(self, voice_input: str) -> Optional[str]:
        """Extract target dog from voice input"""
        # Check for specific dog names
        if re.search(r'\btom\b', voice_input):
            return 'tom'
        elif re.search(r'\bjerry\b', voice_input):
            return 'jerry'
        elif re.search(r'\b(both|all|everyone|together)\b', voice_input):
            return 'both'
        
        return None
    
    def _match_command(self, voice_input: str) -> Optional[Dict]:
        """Match voice input to a command pattern"""
        best_match = None
        best_score = 0
        
        for command_name, command_info in self.command_patterns.items():
            for pattern in command_info['patterns']:
                if re.match(pattern, voice_input, re.IGNORECASE):
                    # Calculate match strength based on pattern specificity
                    score = len(pattern.replace(r'.*\b', '').replace(r'\b.*', ''))
                    if score > best_score:
                        best_score = score
                        best_match = command_info
        
        return best_match
    
    def _calculate_confidence(self, voice_input: str, command_info: Dict) -> float:
        """Calculate confidence score for the matched command"""
        # Simple confidence calculation based on word overlap
        command_words = set()
        for pattern in command_info['patterns']:
            # Extract words from pattern
            words = re.findall(r'\b\w+\b', pattern.lower())
            command_words.update(words)
        
        input_words = set(voice_input.lower().split())
        
        if not command_words:
            return 0.5
        
        overlap = len(command_words.intersection(input_words))
        confidence = overlap / len(command_words)
        
        return min(confidence, 1.0)
    
    def add_custom_command(self, name: str, patterns: List[str], 
                          command_type: CommandType, action: str):
        """Add a custom command pattern"""
        self.command_patterns[name] = {
            'patterns': [f'.*\\b({pattern})\\b.*' for pattern in patterns],
            'type': command_type,
            'action': action
        }
        logger.info(f"Added custom command: {name}")
    
    def get_available_commands(self) -> Dict:
        """Get list of all available commands"""
        commands_by_type = {}
        
        for name, info in self.command_patterns.items():
            cmd_type = info['type'].value
            if cmd_type not in commands_by_type:
                commands_by_type[cmd_type] = []
            
            commands_by_type[cmd_type].append({
                'name': name,
                'action': info['action'],
                'examples': [p.replace('.*\\b', '').replace('\\b.*', '') 
                           for p in info['patterns'][:2]]  # Show first 2 patterns as examples
            })
        
        return commands_by_type
    
    def suggest_corrections(self, voice_input: str) -> List[str]:
        """Suggest possible corrections for unrecognized commands"""
        suggestions = []
        input_words = set(voice_input.lower().split())
        
        for command_name, command_info in self.command_patterns.items():
            command_words = set()
            for pattern in command_info['patterns']:
                words = re.findall(r'\b\w+\b', pattern.lower())
                command_words.update(words)
            
            # Calculate similarity
            if command_words:
                similarity = len(input_words.intersection(command_words)) / len(command_words)
                if similarity > 0.3:  # Threshold for suggestions
                    suggestions.append((command_name, similarity))
        
        # Sort by similarity and return top 3
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return [cmd[0] for cmd in suggestions[:3]]

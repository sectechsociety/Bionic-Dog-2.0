"""
Enhanced Bionic Dog Controller
Integrates Voice Control, Object Following, and Dog-to-Dog Communication
"""

from flask import Flask, render_template, request, jsonify, Response
import threading
import time
import json
import sys
import os
from datetime import datetime
import logging

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our feature modules
try:
    # Try importing utils first (most likely to succeed)
    from utils.helpers import (
        send_dog_command, 
        send_command_to_both_dogs, 
        validate_all_connections,
        setup_logging,
        Timer
    )
    utils_imported = True
except ImportError as e:
    print(f"Warning: utils.helpers import failed: {e}")
    utils_imported = False

try:
    from config.settings import DOG_URLS, VOICE_CONTROL, OBJECT_DETECTION
    config_imported = True
except ImportError as e:
    print(f"Warning: config.settings import failed: {e}")
    config_imported = False
    # Default configurations
    DOG_URLS = {
        'tom': "http://192.168.30.42/control",
        'jerry': "http://192.168.30.153/control"
    }
    VOICE_CONTROL = {'enabled': True}
    OBJECT_DETECTION = {'enabled': True}

try:
    from features.voice_control.voice_controller import VoiceController
    voice_imported = True
except ImportError as e:
    print(f"Warning: VoiceController import failed: {e}")
    voice_imported = False

try:
    from features.communication.message_handler import MessageHandler
    comm_imported = True
except ImportError as e:
    print(f"Warning: MessageHandler import failed: {e}")
    comm_imported = False

try:
    from features.object_following.following_behavior import FollowingBehavior
    following_imported = True
except ImportError as e:
    print(f"Warning: FollowingBehavior import failed: {e}")
    following_imported = False

# Create placeholder functions and classes for failed imports
if not utils_imported:
    def send_dog_command(dog_name, action, **kwargs):
        print(f"Placeholder: Would send {action} to {dog_name}")
        return True
    
    def send_command_to_both_dogs(action):
        print(f"Placeholder: Would send {action} to both dogs")
        return True, True
    
    def validate_all_connections():
        print("Placeholder: Connection validation not available")
        return {'tom': False, 'jerry': False}
    
    def setup_logging(level='INFO', log_file=None):
        import logging
        logging.basicConfig(level=getattr(logging, level))
    
    class Timer:
        def __init__(self): pass
        def start(self): pass
        def stop(self): return 0
        def elapsed(self): return 0

if not voice_imported:
    class VoiceController:
        def __init__(self): pass
        def start_voice_control(self): return False
        def stop_voice_control(self): pass
        def get_command_history(self): return []

if not comm_imported:
    class MessageHandler:
        def __init__(self): pass
        def send_sync_command(self, target, action, delay=0): return True
        def send_message(self, from_dog, to_dog, msg_type, content): return True

if not following_imported:
    class FollowingBehavior:
        def __init__(self): pass
        def start_following(self, **kwargs): return True
        def stop_following(self): pass
        def get_current_status(self): return {'is_active': False}

# Setup logging
try:
    setup_logging('INFO', 'logs/bionic_dog.log')
except:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'bionic_dog_secret_2025'

# Global feature instances
voice_controller = None
message_handler = None
following_behavior = None

# Global state
app_state = {
    'voice_active': False,
    'following_active': False,
    'communication_active': False,
    'last_command': None,
    'dog_status': {'tom': 'idle', 'jerry': 'idle'},
    'connection_status': {'tom': False, 'jerry': False},
    'session_stats': {
        'commands_sent': 0,
        'voice_commands': 0,
        'sync_actions': 0,
        'start_time': datetime.now()
    }
}

def initialize_features():
    """Initialize all feature modules"""
    global voice_controller, message_handler, following_behavior
    
    try:
        # Initialize voice controller with callback
        def voice_command_callback(dog_name, action):
            return send_dog_command(dog_name, action)
            
        voice_controller = VoiceController(voice_command_callback)
        logger.info("Voice controller initialized")
        
        # Initialize message handler
        message_handler = MessageHandler()
        logger.info("Message handler initialized")
        
        # Initialize object following with callback
        def following_command_callback(dog_name, action):
            return send_dog_command(dog_name, action)
            
        following_behavior = FollowingBehavior(following_command_callback)
        logger.info("Object following initialized")
        
        # Test connections
        try:
            connections = validate_all_connections()
            app_state['connection_status'].update(connections)
            logger.info(f"Connection status: {connections}")
        except Exception as e:
            logger.warning(f"Connection test failed: {e}")
            app_state['connection_status'] = {'tom': False, 'jerry': False}
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize features: {str(e)}")
        return False

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('enhanced_dashboard.html', 
                         app_state=app_state, 
                         dog_urls=DOG_URLS if 'DOG_URLS' in globals() else {'tom': '', 'jerry': ''})

# ================== BASIC DOG CONTROLS ==================
@app.route('/control/<dog_name>/<action>', methods=['POST'])
def control_dog(dog_name, action):
    """Basic dog control endpoint"""
    try:
        success = send_dog_command(dog_name, action)
        app_state['last_command'] = {
            'dog': dog_name,
            'action': action,
            'timestamp': datetime.now().isoformat(),
            'success': success
        }
        app_state['session_stats']['commands_sent'] += 1
        
        if success:
            app_state['dog_status'][dog_name] = action
            
        return jsonify({
            'status': 'success' if success else 'error',
            'dog': dog_name,
            'action': action,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Control error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/control/both/<action>', methods=['POST'])
def control_both_dogs(action):
    """Control both dogs simultaneously"""
    try:
        tom_success, jerry_success = send_command_to_both_dogs(action)
        
        app_state['last_command'] = {
            'dog': 'both',
            'action': action,
            'timestamp': datetime.now().isoformat(),
            'success': tom_success and jerry_success
        }
        app_state['session_stats']['commands_sent'] += 1
        
        if tom_success:
            app_state['dog_status']['tom'] = action
        if jerry_success:
            app_state['dog_status']['jerry'] = action
            
        return jsonify({
            'status': 'success' if (tom_success and jerry_success) else 'partial',
            'tom_success': tom_success,
            'jerry_success': jerry_success,
            'action': action,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Both control error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ================== VOICE CONTROL ENDPOINTS ==================
@app.route('/api/voice/start', methods=['POST'])
def start_voice_control():
    """Start voice command recognition"""
    try:
        if voice_controller and not app_state['voice_active']:
            success = voice_controller.start_voice_control()
            if success:
                app_state['voice_active'] = True
                return jsonify({
                    'status': 'success', 
                    'message': 'Voice control started',
                    'active': True
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Failed to start voice control'
                })
        else:
            return jsonify({
                'status': 'info', 
                'message': 'Voice control already active',
                'active': app_state['voice_active']
            })
            
    except Exception as e:
        logger.error(f"Voice start error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/voice/stop', methods=['POST'])
def stop_voice_control():
    """Stop voice command recognition"""
    try:
        if voice_controller and app_state['voice_active']:
            voice_controller.stop_voice_control()
            app_state['voice_active'] = False
            
            return jsonify({
                'status': 'success', 
                'message': 'Voice control stopped',
                'active': False
            })
        else:
            return jsonify({
                'status': 'info', 
                'message': 'Voice control not active',
                'active': False
            })
            
    except Exception as e:
        logger.error(f"Voice stop error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/voice/status')
def voice_status():
    """Get voice control status"""
    try:
        history = voice_controller.get_command_history(5) if voice_controller else []
        available_commands = voice_controller.get_available_commands() if voice_controller else {}
        
        return jsonify({
            'active': app_state['voice_active'],
            'last_commands': history,
            'available_commands': available_commands,
            'total_voice_commands': app_state['session_stats']['voice_commands']
        })
    except Exception as e:
        return jsonify({'active': False, 'error': str(e)})

# ================== OBJECT FOLLOWING ENDPOINTS ==================
@app.route('/api/following/start', methods=['POST'])
def start_object_following():
    """Start object following"""
    try:
        data = request.get_json() or {}
        target_type = data.get('target_type', 'face')
        dog_name = data.get('dog', 'tom')
        
        if following_behavior and not app_state['following_active']:
            from features.object_following.object_detector import DetectionMethod
            from features.object_following.tracking_controller import TrackingMode
            
            # Map string to enum
            detection_methods = {
                'face': DetectionMethod.FACE_DETECTION,
                'color': DetectionMethod.COLOR_TRACKING,
                'red': DetectionMethod.COLOR_TRACKING,
                'blue': DetectionMethod.COLOR_TRACKING,
                'green': DetectionMethod.COLOR_TRACKING,
            }
            
            method = detection_methods.get(target_type, DetectionMethod.FACE_DETECTION)
            
            success = following_behavior.start_following(
                target_dog=dog_name,
                detection_method=method,
                tracking_mode=TrackingMode.FOLLOW
            )
            
            if success:
                app_state['following_active'] = True
                return jsonify({
                    'status': 'success',
                    'message': f'Object following started for {dog_name}',
                    'target_type': target_type,
                    'dog': dog_name,
                    'active': True
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Failed to start object following'
                })
        else:
            return jsonify({
                'status': 'info',
                'message': 'Object following already active',
                'active': app_state['following_active']
            })
            
    except Exception as e:
        logger.error(f"Following start error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/following/stop', methods=['POST'])
def stop_object_following():
    """Stop object following"""
    try:
        if following_behavior and app_state['following_active']:
            following_behavior.stop_following()
            app_state['following_active'] = False
            
            return jsonify({
                'status': 'success',
                'message': 'Object following stopped',
                'active': False
            })
        else:
            return jsonify({
                'status': 'info',
                'message': 'Object following not active',
                'active': False
            })
            
    except Exception as e:
        logger.error(f"Following stop error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/following/status')
def following_status():
    """Get object following status"""
    try:
        if following_behavior:
            status = following_behavior.get_current_status()
            return jsonify({
                'active': app_state['following_active'],
                'status': status,
                'available_targets': ['face', 'red', 'blue', 'green']
            })
        else:
            return jsonify({'active': False, 'status': {}, 'available_targets': []})
    except Exception as e:
        return jsonify({'active': False, 'error': str(e)})

# ================== DOG-TO-DOG COMMUNICATION ENDPOINTS ==================
@app.route('/api/communication/start', methods=['POST'])
def start_communication():
    """Start dog-to-dog communication"""
    try:
        if message_handler and not app_state['communication_active']:
            app_state['communication_active'] = True
            
            return jsonify({
                'status': 'success',
                'message': 'Dog-to-dog communication started',
                'active': True
            })
        else:
            return jsonify({
                'status': 'info',
                'message': 'Communication already active',
                'active': app_state['communication_active']
            })
            
    except Exception as e:
        logger.error(f"Communication start error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/communication/sync', methods=['POST'])
def sync_dogs():
    """Send synchronized command to both dogs"""
    try:
        data = request.get_json() or {}
        action = data.get('action')
        delay_ms = data.get('delay_ms', 0)
        
        if not action:
            return jsonify({'status': 'error', 'message': 'Action required'}), 400
            
        if message_handler and app_state['communication_active']:
            # Use message handler for coordination
            success = message_handler.send_message('controller', 'both', 'sync_command', {
                'action': action,
                'delay_ms': delay_ms
            })
            
            # Also send direct commands as fallback
            if success:
                tom_success, jerry_success = send_command_to_both_dogs(action)
                success = tom_success and jerry_success
            
            app_state['session_stats']['sync_actions'] += 1
            
            return jsonify({
                'status': 'success' if success else 'error',
                'message': f'Sync command {"sent" if success else "failed"}: {action}',
                'action': action,
                'delay_ms': delay_ms
            })
        else:
            # Fallback to basic synchronization
            tom_success, jerry_success = send_command_to_both_dogs(action)
            success = tom_success and jerry_success
            
            return jsonify({
                'status': 'success' if success else 'error',
                'message': f'Basic sync {"sent" if success else "failed"}: {action}',
                'method': 'basic'
            })
            
    except Exception as e:
        logger.error(f"Sync error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/communication/send_message', methods=['POST'])
def send_message():
    """Send custom message between dogs"""
    try:
        data = request.get_json() or {}
        from_dog = data.get('from', 'tom')
        to_dog = data.get('to', 'jerry')
        message_type = data.get('type', 'status')
        content = data.get('content', {})
        
        if message_handler and app_state['communication_active']:
            success = message_handler.send_message(from_dog, to_dog, message_type, content)
            
            return jsonify({
                'status': 'success' if success else 'error',
                'message': f'Message {"sent" if success else "failed"}',
                'from': from_dog,
                'to': to_dog,
                'type': message_type
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Communication not active'
            }), 400
            
    except Exception as e:
        logger.error(f"Message send error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ================== STATUS AND MONITORING ==================
@app.route('/api/status')
def get_status():
    """Get complete system status"""
    try:
        connections = validate_all_connections()
        app_state['connection_status'].update(connections)
    except Exception as e:
        logger.warning(f"Connection check failed: {e}")
    
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'features': {
            'voice_control': app_state['voice_active'],
            'object_following': app_state['following_active'],
            'communication': app_state['communication_active']
        },
        'connections': app_state['connection_status'],
        'dog_status': app_state['dog_status'],
        'last_command': app_state['last_command'],
        'session_stats': app_state['session_stats']
    })

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'features_initialized': all([
            voice_controller is not None,
            message_handler is not None,
            following_behavior is not None
        ]),
        'uptime_seconds': (datetime.now() - app_state['session_stats']['start_time']).total_seconds()
    })

# ================== SPECIAL CHOREOGRAPHY ==================
@app.route('/choreography/handshake')
def perform_handshake():
    """Enhanced handshake choreography using communication"""
    try:
        if message_handler and app_state['communication_active']:
            # Use synchronized communication
            success = message_handler.broadcast_message('controller', 'coordinate_action', {
                'action': 'handshake_sequence',
                'participants': ['tom', 'jerry']
            })
        
        # Execute the actual handshake sequence
        tom_success, jerry_success = send_command_to_both_dogs('forward')
        time.sleep(1)
        tom_success2, jerry_success2 = send_command_to_both_dogs('handshake')
        time.sleep(2)
        send_command_to_both_dogs('stop')
        
        success = tom_success and jerry_success and tom_success2 and jerry_success2
            
        return jsonify({
            'status': 'success' if success else 'error',
            'choreography': 'handshake',
            'method': 'synchronized' if app_state['communication_active'] else 'basic'
        })
        
    except Exception as e:
        logger.error(f"Handshake error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/choreography/disco')
def perform_disco():
    """Enhanced disco choreography"""
    try:
        if message_handler and app_state['communication_active']:
            success = message_handler.broadcast_message('controller', 'coordinate_action', {
                'action': 'disco_sequence',
                'participants': ['tom', 'jerry']
            })
        
        # Execute disco sequence
        send_command_to_both_dogs('ssdance')
        time.sleep(3)
        success = send_command_to_both_dogs('hiphop')
            
        return jsonify({
            'status': 'success' if success else 'error',
            'choreography': 'disco',
            'method': 'synchronized' if app_state['communication_active'] else 'basic'
        })
        
    except Exception as e:
        logger.error(f"Disco error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/choreography/mirror')
def perform_mirror():
    """Mirror dance choreography"""
    try:
        # Mirror sequence - one dog does opposite of the other
        send_dog_command('tom', 'left')
        send_dog_command('jerry', 'right')
        time.sleep(1)
        
        send_dog_command('tom', 'bow')
        send_dog_command('jerry', 'jump')
        time.sleep(2)
        
        send_command_to_both_dogs('steady')
        
        return jsonify({
            'status': 'success',
            'choreography': 'mirror'
        })
        
    except Exception as e:
        logger.error(f"Mirror error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/choreography/chase')
def perform_chase():
    """Chase game choreography"""
    try:
        # Simple chase sequence
        send_dog_command('tom', 'forward')
        time.sleep(0.5)
        send_dog_command('jerry', 'forward')
        time.sleep(1)
        
        send_dog_command('tom', 'right')
        send_dog_command('jerry', 'left')
        time.sleep(1)
        
        send_command_to_both_dogs('jump')
        time.sleep(1)
        send_command_to_both_dogs('stop')
        
        return jsonify({
            'status': 'success',
            'choreography': 'chase'
        })
        
    except Exception as e:
        logger.error(f"Chase error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ================== VIDEO STREAMING ==================
@app.route('/video_feed/<dog_name>')
def video_feed(dog_name):
    """Video feed endpoint (placeholder for camera integration)"""
    camera_urls = {
        'tom': "http://10.243.146.17:5000/video_feed",
        'jerry': None  # Add when available
    }
    
    return jsonify({
        'message': f'Video feed for {dog_name}',
        'dog': dog_name,
        'camera_url': camera_urls.get(dog_name),
        'status': 'available' if camera_urls.get(dog_name) else 'not_available'
    })

# ================== ERROR HANDLERS ==================
@app.errorhandler(404)
def not_found(error):
    return jsonify({'status': 'error', 'message': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

if __name__ == '__main__':
    # Initialize features on startup
    logger.info("Starting Enhanced Bionic Dog Controller...")
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    if initialize_features():
        logger.info("All features initialized successfully")
    else:
        logger.warning("Some features failed to initialize, but app will continue")
    
    # Start the Flask app
    logger.info("Starting Flask server on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)

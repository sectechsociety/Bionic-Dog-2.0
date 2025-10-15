"""
Speech Recognition Engine
Handles audio input and converts speech to text for command processing
"""

import speech_recognition as sr
import pyaudio
import threading
import queue
import logging
from typing import Optional, Callable

logger = logging.getLogger(__name__)

class SpeechRecognizer:
    """Speech recognition engine for voice commands"""
    
    def __init__(self, language='en-US', energy_threshold=300):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.language = language
        self.is_listening = False
        self.audio_queue = queue.Queue()
        self.recognition_thread = None
        
        # Configure recognizer
        self.recognizer.energy_threshold = energy_threshold
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
        # Callbacks
        self.on_command_recognized = None
        self.on_listening_started = None
        self.on_listening_stopped = None
        
        # Calibrate microphone
        self._calibrate_microphone()
    
    def _calibrate_microphone(self):
        """Calibrate microphone for ambient noise"""
        try:
            with self.microphone as source:
                logger.info("Calibrating microphone for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            logger.info("Microphone calibrated successfully")
        except Exception as e:
            logger.error(f"Failed to calibrate microphone: {str(e)}")
    
    def start_listening(self, callback: Callable[[str], None] = None):
        """Start continuous listening for voice commands"""
        if self.is_listening:
            logger.warning("Already listening for commands")
            return
        
        self.is_listening = True
        self.on_command_recognized = callback
        
        # Start listening thread
        self.recognition_thread = threading.Thread(target=self._listen_continuously)
        self.recognition_thread.daemon = True
        self.recognition_thread.start()
        
        if self.on_listening_started:
            self.on_listening_started()
        
        logger.info("Started listening for voice commands")
    
    def stop_listening(self):
        """Stop listening for voice commands"""
        self.is_listening = False
        
        if self.recognition_thread and self.recognition_thread.is_alive():
            self.recognition_thread.join(timeout=2)
        
        if self.on_listening_stopped:
            self.on_listening_stopped()
        
        logger.info("Stopped listening for voice commands")
    
    def _listen_continuously(self):
        """Continuous listening loop"""
        with self.microphone as source:
            while self.is_listening:
                try:
                    # Listen for audio with timeout
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
                    
                    # Add to queue for processing
                    self.audio_queue.put(audio)
                    
                    # Process in separate thread to avoid blocking
                    processing_thread = threading.Thread(target=self._process_audio, args=(audio,))
                    processing_thread.daemon = True
                    processing_thread.start()
                    
                except sr.WaitTimeoutError:
                    # Timeout is normal, continue listening
                    continue
                except Exception as e:
                    logger.error(f"Error during listening: {str(e)}")
                    continue
    
    def _process_audio(self, audio):
        """Process audio and recognize speech"""
        try:
            # Use Google Speech Recognition
            text = self.recognizer.recognize_google(audio, language=self.language)
            logger.info(f"Recognized speech: '{text}'")
            
            if self.on_command_recognized:
                self.on_command_recognized(text.lower().strip())
                
        except sr.UnknownValueError:
            # Speech was unintelligible
            logger.debug("Could not understand audio")
        except sr.RequestError as e:
            logger.error(f"Speech recognition service error: {str(e)}")
        except Exception as e:
            logger.error(f"Error processing audio: {str(e)}")
    
    def recognize_from_file(self, audio_file_path: str) -> Optional[str]:
        """Recognize speech from an audio file"""
        try:
            with sr.AudioFile(audio_file_path) as source:
                audio = self.recognizer.record(source)
            
            text = self.recognizer.recognize_google(audio, language=self.language)
            logger.info(f"Recognized from file: '{text}'")
            return text.lower().strip()
            
        except Exception as e:
            logger.error(f"Failed to recognize speech from file: {str(e)}")
            return None
    
    def set_language(self, language: str):
        """Set recognition language"""
        self.language = language
        logger.info(f"Speech recognition language set to: {language}")
    
    def adjust_sensitivity(self, energy_threshold: int):
        """Adjust microphone sensitivity"""
        self.recognizer.energy_threshold = energy_threshold
        logger.info(f"Microphone sensitivity adjusted to: {energy_threshold}")
    
    def test_microphone(self) -> bool:
        """Test if microphone is working"""
        try:
            with self.microphone as source:
                logger.info("Testing microphone... Say something!")
                audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=2)
                text = self.recognizer.recognize_google(audio)
                logger.info(f"Microphone test successful. Heard: '{text}'")
                return True
        except Exception as e:
            logger.error(f"Microphone test failed: {str(e)}")
            return False

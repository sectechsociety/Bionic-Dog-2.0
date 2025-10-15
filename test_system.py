#!/usr/bin/env python3
"""
Test script for Enhanced Bionic Dog Controller
Tests basic functionality without requiring all dependencies
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if core modules can be imported"""
    print("Testing imports...")
    
    # Test basic imports
    try:
        import flask
        print("✅ Flask available")
    except ImportError:
        print("❌ Flask not installed - run: pip install flask")
    
    try:
        import requests
        print("✅ Requests available")
    except ImportError:
        print("❌ Requests not installed - run: pip install requests")
    
    # Test our modules
    try:
        from utils.helpers import send_dog_command, setup_logging
        print("✅ Helper functions loaded")
    except ImportError as e:
        print(f"❌ Helper functions failed: {e}")
    
    try:
        from config.settings import DOG_URLS
        print("✅ Configuration loaded")
    except ImportError as e:
        print(f"❌ Configuration failed: {e}")
    
    print()

def test_basic_functionality():
    """Test basic functionality without hardware"""
    print("Testing basic functionality...")
    
    try:
        from utils.helpers import setup_logging
        setup_logging('INFO')
        print("✅ Logging setup successful")
    except Exception as e:
        print(f"❌ Logging setup failed: {e}")
    
    try:
        from config.settings import DOG_URLS
        print(f"✅ Dog URLs configured: {list(DOG_URLS.keys())}")
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
    
    print()

def test_web_interface():
    """Test if web interface can be imported"""
    print("Testing web interface...")
    
    try:
        # Import main application
        from enhanced_dog_controller import app
        print("✅ Flask application imported successfully")
        
        # Test if we can create test client
        with app.test_client() as client:
            response = client.get('/api/health')
            if response.status_code == 200:
                print("✅ Health endpoint working")
            else:
                print(f"⚠️ Health endpoint returned {response.status_code}")
                
    except ImportError as e:
        print(f"❌ Flask application import failed: {e}")
    except Exception as e:
        print(f"⚠️ Web interface test failed: {e}")
    
    print()

def check_optional_dependencies():
    """Check optional dependencies for advanced features"""
    print("Checking optional dependencies...")
    
    # Voice control dependencies
    try:
        import speech_recognition
        print("✅ SpeechRecognition available - Voice control ready")
    except ImportError:
        print("⚠️ SpeechRecognition not installed - Voice control disabled")
        print("   Install with: pip install SpeechRecognition")
    
    try:
        import pyaudio
        print("✅ PyAudio available - Microphone ready")
    except ImportError:
        print("⚠️ PyAudio not installed - Microphone disabled")
        print("   Install with: pip install pyaudio")
    
    # Computer vision dependencies
    try:
        import cv2
        print("✅ OpenCV available - Object following ready")
    except ImportError:
        print("⚠️ OpenCV not installed - Object following disabled")
        print("   Install with: pip install opencv-python")
    
    try:
        import numpy
        print("✅ NumPy available - Image processing ready")
    except ImportError:
        print("⚠️ NumPy not installed - Image processing disabled")
        print("   Install with: pip install numpy")
    
    print()

def main():
    print("🐕 Enhanced Bionic Dog Controller - Test Suite 🤖")
    print("=" * 50)
    
    test_imports()
    test_basic_functionality()
    test_web_interface()
    check_optional_dependencies()
    
    print("Test Summary:")
    print("- If Flask and requests are available, basic dog control will work")
    print("- Optional dependencies enable advanced features")
    print("- Run 'python enhanced_dog_controller.py' to start the server")
    print("- Access dashboard at: http://localhost:5000")
    print()
    print("To install all dependencies, run:")
    print("pip install -r requirements.txt")

if __name__ == '__main__':
    main()

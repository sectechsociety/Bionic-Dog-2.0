#!/usr/bin/env python3
"""
Bionic Dog 2.0 Startup Script
Easy launcher for the Enhanced Bionic Dog Controller
"""

import os
import sys
import subprocess
import webbrowser
import time

def print_banner():
    print("🐕" + "="*50 + "🤖")
    print("    Enhanced Bionic Dog Controller 2.0")
    print("         Starting Up...")
    print("🐕" + "="*50 + "🤖")

def check_dependencies():
    """Check and install critical dependencies"""
    required = ['flask', 'requests']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing required packages: {', '.join(missing)}")
        print("Installing required packages...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing)
            print("✅ Required packages installed!")
        except subprocess.CalledProcessError:
            print("❌ Failed to install packages. Please run:")
            print(f"pip install {' '.join(missing)}")
            return False
    
    return True

def check_optional_dependencies():
    """Check optional dependencies and show status"""
    optional = {
        'opencv-python': 'Object Following',
        'SpeechRecognition': 'Voice Control', 
        'pyaudio': 'Microphone Input',
        'numpy': 'Image Processing'
    }
    
    available = []
    missing = []
    
    for package, feature in optional.items():
        try:
            if package == 'opencv-python':
                import cv2
            elif package == 'SpeechRecognition':
                import speech_recognition
            elif package == 'pyaudio':
                import pyaudio
            elif package == 'numpy':
                import numpy
            available.append(f"✅ {feature}")
        except ImportError:
            missing.append(f"⚠️  {feature} (install {package})")
    
    if available:
        print("\nAvailable Features:")
        for feature in available:
            print(f"  {feature}")
    
    if missing:
        print("\nOptional Features (install to enable):")
        for feature in missing:
            print(f"  {feature}")

def start_server():
    """Start the Flask server"""
    print("\n🚀 Starting Enhanced Bionic Dog Controller...")
    
    # Change to project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    # Start server in background
    try:
        import enhanced_dog_controller
        print("✅ Server module loaded successfully")
        
        # Open browser after short delay
        def open_browser():
            time.sleep(2)
            print("🌐 Opening dashboard in browser...")
            webbrowser.open('http://localhost:5000')
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        print("✅ Server starting on http://localhost:5000")
        print("✅ Dashboard will open automatically")
        print("\nPress Ctrl+C to stop the server")
        print("-" * 50)
        
        # Start Flask app
        enhanced_dog_controller.app.run(
            host='0.0.0.0', 
            port=5000, 
            debug=False,  # Disable debug for cleaner output
            threaded=True
        )
        
    except ImportError as e:
        print(f"❌ Failed to import server module: {e}")
        print("Make sure all files are in the correct location")
        return False
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")
        return True
    except Exception as e:
        print(f"❌ Server error: {e}")
        return False

def main():
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Cannot start without required dependencies")
        return
    
    # Show optional features status
    check_optional_dependencies()
    
    print("\n" + "="*50)
    
    # Start server
    start_server()

if __name__ == '__main__':
    main()

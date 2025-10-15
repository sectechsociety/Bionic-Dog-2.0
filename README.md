# 🐕 Enhanced Bionic Dog Controller 2.0 🤖

An advanced control system for bionic dogs with **Voice Commands**, **Object Following**, and **Dog-to-Dog Communication**.

## 🚀 Features

### 🎙️ Voice Command Recognition
- Natural language processing for voice commands
- Support for individual and group commands
- Real-time speech-to-text conversion
- Customizable command patterns

### 👁️ Object Following  
- Computer vision-based object tracking
- Multiple detection methods (face, color, template)
- Autonomous following behaviors
- PID-controlled smooth movements

### 📡 Dog-to-Dog Communication
- Synchronized command execution
- Message passing between dogs
- Coordinated choreography sequences
- Formation control

### 🎮 Enhanced Web Interface
- Modern responsive dashboard
- Real-time status monitoring  
- Interactive control panels
- Session statistics

## 📋 Requirements

### Core Dependencies (Required)
```bash
pip install flask requests
```

### Voice Control Dependencies
```bash
pip install SpeechRecognition pyaudio pyttsx3
```

### Computer Vision Dependencies
```bash
pip install opencv-python numpy Pillow
```

### Full Installation
```bash
pip install -r requirements.txt
```

## 🛠️ Installation

1. **Clone or download the project**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Test the system:**
   ```bash
   python test_system.py
   ```
4. **Start the server:**
   ```bash
   python enhanced_dog_controller.py
   ```
5. **Open dashboard:** http://localhost:5000

## 🎯 Quick Start

### Basic Dog Control
1. Open the web dashboard
2. Select dog (Tom, Jerry, or Both)
3. Use movement buttons or action commands
4. Monitor real-time status

### Voice Control
1. Click "Voice Recognition" toggle
2. Grant microphone permissions
3. Say commands like:
   - "Tom forward"
   - "Jerry dance"
   - "Both dogs stop"
   - "Perform handshake"

### Object Following
1. Select target type (Face, Red, Blue, Green)
2. Choose which dog should follow
3. Click "Start Following"
4. Dog will automatically track and follow objects

### Synchronized Actions
1. Enable "Dog-to-Dog Communication"
2. Select synchronized action
3. Click "Execute Synchronized"
4. Watch coordinated movements

## 🌐 API Endpoints

### Basic Control
- `POST /control/{dog_name}/{action}` - Control individual dog
- `POST /control/both/{action}` - Control both dogs

### Voice Control
- `POST /api/voice/start` - Start voice recognition
- `POST /api/voice/stop` - Stop voice recognition
- `GET /api/voice/status` - Get voice control status

### Object Following
- `POST /api/following/start` - Start object following
- `POST /api/following/stop` - Stop object following
- `GET /api/following/status` - Get following status

### Communication
- `POST /api/communication/start` - Start communication
- `POST /api/communication/sync` - Send sync command
- `POST /api/communication/send_message` - Send custom message

### Status
- `GET /api/status` - Get complete system status
- `GET /api/health` - Health check

## 🎪 Choreography

### Available Sequences
- **Enhanced Handshake** - `/choreography/handshake`
- **Disco Party** - `/choreography/disco`  
- **Mirror Dance** - `/choreography/mirror`
- **Chase Game** - `/choreography/chase`

## ⚙️ Configuration

Edit `config/settings.py` to customize:

```python
# Dog connection URLs
DOG_URLS = {
    'tom': "http://192.168.30.42/control",
    'jerry': "http://192.168.30.153/control"
}

# Camera settings
CAMERA_SETTINGS = {
    'tom_camera_url': "http://10.243.146.17:5000/video_feed",
    'default_resolution': (640, 480)
}

# Voice control settings
VOICE_CONTROL = {
    'language': 'en-US',
    'energy_threshold': 300
}
```

## 🔧 Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# Install missing dependencies
pip install flask requests opencv-python SpeechRecognition
```

**2. Microphone Not Working**
```bash
# Install audio dependencies
pip install pyaudio
# On Linux: sudo apt-get install portaudio19-dev
# On Windows: Use precompiled wheels
```

**3. Camera Not Detected**
```bash
# Install OpenCV
pip install opencv-python
# Check camera permissions
```

**4. Dogs Not Responding**
- Check network connectivity
- Verify dog IP addresses in config
- Test with basic HTTP requests

## 🎯 Quick Test

Run the test script to verify everything is working:
```bash
python test_system.py
```

## 📁 Project Structure

```
Bionic-Dog-2.0/
├── enhanced_dog_controller.py    # Main Flask application
├── test_system.py               # System test script
├── requirements.txt             # Python dependencies
├── templates/
│   └── enhanced_dashboard.html  # Web interface
├── features/
│   ├── voice_control/          # Voice command modules
│   ├── communication/          # Dog-to-dog communication
│   └── object_following/       # Computer vision modules
├── config/
│   └── settings.py            # Configuration file
├── utils/
│   └── helpers.py             # Utility functions
└── logs/                      # Log files
```

## 🚀 Getting Started

1. **Install Flask and Requests (minimum):**
   ```bash
   pip install flask requests
   ```

2. **Run the system test:**
   ```bash
   python test_system.py
   ```

3. **Start the server:**
   ```bash
   python enhanced_dog_controller.py
   ```

4. **Open your browser to:**
   ```
   http://localhost:5000
   ```

5. **Install optional features as needed:**
   ```bash
   pip install opencv-python SpeechRecognition pyaudio
   ```

---

**🐕 Ready to control your bionic dogs with advanced AI features! 🤖**
Not an Ordinary Bionic Dog

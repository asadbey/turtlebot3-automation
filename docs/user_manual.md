# User Manual

This comprehensive user manual covers how to operate the TurtleBot3 automation system effectively.

## Table of Contents

- [Getting Started](#getting-started)
- [Basic Operations](#basic-operations)
- [Navigation](#navigation)
- [Object Detection](#object-detection)
- [Voice Control](#voice-control)
- [System Monitoring](#system-monitoring)
- [Configuration](#configuration)
- [Advanced Features](#advanced-features)
- [Troubleshooting](#troubleshooting)

## Getting Started

### Quick Start Guide

For users who want to get running quickly:

```bash
# 1. Launch the system
python turtlebot_automation.py

# 2. The system will:
#    - Initialize all modules
#    - Start simulation (if enabled)
#    - Begin health monitoring
#    - Launch navigation and detection
#    - Activate voice control
```

### First Time Setup

1. **Environment Setup**
   ```bash
   source /opt/ros/humble/setup.bash
   export TURTLEBOT3_MODEL=waffle
   ```

2. **Launch Simulation**
   ```bash
   python turtlebot_automation.py --module setup
   python turtlebot_automation.py
   ```

3. **Verify Operation**
   - Gazebo window opens with TurtleBot3
   - RViz shows robot and sensors
   - Terminal shows system status

### Understanding the Interface

The system provides multiple interfaces:

- **Terminal Output**: Real-time status and logs
- **Gazebo Window**: 3D simulation environment
- **RViz**: Visualization and control interface
- **Voice**: Audio feedback and command input

## Basic Operations

### Starting the System

#### Full Automation Mode

```bash
# Start all modules
python turtlebot_automation.py

# With custom configuration
python turtlebot_automation.py --config config/my_config.yaml

# Hardware mode (no simulation)
python turtlebot_automation.py --no-simulation
```

#### Individual Module Mode

```bash
# Setup only
python turtlebot_automation.py --module setup

# Navigation only
python turtlebot_automation.py --module navigation

# Object detection only
python turtlebot_automation.py --module detection

# Voice control only
python turtlebot_automation.py --module voice

# Maintenance monitoring only
python turtlebot_automation.py --module maintenance
```

### Stopping the System

- **Keyboard Interrupt**: Press `Ctrl+C` in terminal
- **Graceful Shutdown**: System will properly close all modules
- **Emergency Stop**: Say "TurtleBot emergency stop" or use `Ctrl+C`

## Navigation

### Autonomous Navigation

#### Basic Navigation

```python
from modules.navigation_automation import NavigationAutomation

# Initialize navigation
nav = NavigationAutomation(config, simulation_mode=True)
nav.initialize()
nav.start_navigation()

# Navigate to specific location
nav.navigate_to_pose(x=2.0, y=3.0, yaw=1.57)
```

#### Waypoint Navigation

```python
# Define multiple waypoints
waypoints = [
    (1.0, 1.0, 0.0),    # x, y, yaw
    (2.0, 2.0, 1.57),
    (3.0, 1.0, 0.0),
    (1.0, 0.0, -1.57)
]

# Follow waypoints
nav.follow_waypoints(waypoints)
```

#### Voice Navigation

```bash
# Voice commands for navigation
"TurtleBot navigate to kitchen"
"TurtleBot go to living room"
"TurtleBot explore"
"TurtleBot go home"
```

### Manual Control

#### Keyboard Teleoperation

```bash
# In separate terminal
ros2 run turtlebot3_teleop teleop_keyboard
```

#### Voice Movement Commands

```bash
# Movement commands
"TurtleBot move forward"
"TurtleBot turn left"
"TurtleBot turn right"
"TurtleBot move backward"
"TurtleBot stop"
```

### Map Management

#### Creating Maps (SLAM)

```bash
# Launch with SLAM enabled
python turtlebot_automation.py --config config/slam_config.yaml

# Or use launch file
ros2 launch turtlebot_automation slam_navigation.launch.py
```

#### Saving Maps

```bash
# Save current map
ros2 run nav2_map_server map_saver_cli -f my_map

# This creates:
# - my_map.yaml (map metadata)
# - my_map.pgm (map image)
```

#### Loading Maps

```bash
# Load existing map for navigation
python turtlebot_automation.py --config config/navigation_config.yaml
```

## Object Detection

### Real-time Detection

The object detection system automatically starts when the full system is launched.

#### Detection Output

```python
# Get detection results
from modules.object_detection import ObjectDetection

detector = ObjectDetection(config)
stats = detector.get_detection_stats()
print(f"Total detections: {stats['total_detections']}")
print(f"Current FPS: {stats['current_fps']}")
```

#### Detection Topics

```bash
# View detection results
ros2 topic echo /object_detections

# View annotated camera feed
ros2 topic echo /detection_image
```

### Custom Detection

#### Testing with Images

```python
# Test detection on specific image
detections = detector.detect_objects_sync("test_image.jpg")

for detection in detections:
    print(f"Object: {detection['class_name']}")
    print(f"Confidence: {detection['confidence']:.2f}")
    print(f"Bounding box: {detection['bbox']}")
```

#### Detection Configuration

```yaml
# config/detection_config.yaml
detection:
  model_path: "yolov8n.pt"  # or yolov8s.pt, yolov8m.pt
  confidence: 0.5              # Detection confidence threshold
  camera_topic: "/camera/image_raw"
  max_detections: 100
```

### Supported Objects

The YOLOv8 model can detect 80 common objects including:

- **Person**: person
- **Vehicles**: bicycle, car, motorcycle, airplane, bus, train, truck
- **Animals**: bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe
- **Objects**: backpack, umbrella, handbag, tie, suitcase, frisbee, skis, snowboard
- **Sports**: baseball bat, baseball glove, skateboard, surfboard, tennis racket
- **Food**: banana, apple, sandwich, orange, broccoli, carrot, hot dog, pizza, donut, cake
- **Household**: chair, couch, potted plant, bed, dining table, toilet, tv, laptop, mouse, remote, keyboard, cell phone, microwave, oven, toaster, sink, refrigerator, book, clock, vase, scissors, teddy bear, hair drier, toothbrush

## Voice Control

### Voice Commands Overview

The voice control system responds to natural language commands starting with "TurtleBot".

### Movement Commands

| Command | Action |
|---------|--------|
| "TurtleBot move forward" | Move robot forward |
| "TurtleBot move backward" | Move robot backward |
| "TurtleBot turn left" | Rotate left |
| "TurtleBot turn right" | Rotate right |
| "TurtleBot stop" | Stop movement |
| "TurtleBot emergency stop" | Immediate stop |

### Navigation Commands

| Command | Action |
|---------|--------|
| "TurtleBot navigate to kitchen" | Navigate to kitchen location |
| "TurtleBot go to living room" | Navigate to living room |
| "TurtleBot explore" | Start exploration mode |
| "TurtleBot go home" | Return to origin |

### Information Commands

| Command | Action |
|---------|--------|
| "TurtleBot what do you see?" | Scan and report detected objects |
| "TurtleBot scan for objects" | Perform object detection scan |
| "TurtleBot status report" | Report system health status |

### Special Commands

| Command | Action |
|---------|--------|
| "TurtleBot follow me" | Start person following mode |
| "TurtleBot stop following" | Stop person following |
| "TurtleBot wake up" | Activate voice control |
| "TurtleBot sleep" | Deactivate voice control |

### Voice Setup

#### Microphone Configuration

```bash
# List available microphones
python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"

# Test microphone
python -c "
import speech_recognition as sr
r = sr.Recognizer()
with sr.Microphone() as source:
    print('Say something!')
    audio = r.listen(source)
    print('You said: ' + r.recognize_google(audio))
"
```

#### Voice Feedback

The system provides audio feedback:

- **Activation**: "Voice control activated"
- **Command Received**: "Navigating to kitchen"
- **Error**: "I didn't understand that command"
- **Status**: "System healthy"

### Custom Voice Commands

#### Adding New Commands

```python
# Extend voice control with custom commands
class CustomVoiceControl(VoiceControl):
    def __init__(self, config):
        super().__init__(config)
        
        # Add custom command patterns
        self.command_patterns.update({
            'dance': r'(dance|do a dance)',
            'sing': r'(sing|play a song)',
            'take_picture': r'(take picture|photo)'
        })
    
    def _process_voice_command(self, command):
        # Handle custom commands
        if self._match_pattern(command, 'dance'):
            self._execute_dance()
        elif self._match_pattern(command, 'sing'):
            self._execute_sing()
        elif self._match_pattern(command, 'take_picture'):
            self._execute_take_picture()
        
        # Call parent for standard commands
        super()._process_voice_command(command)
```

## System Monitoring

### Health Monitoring

The maintenance module continuously monitors system health.

#### Health Metrics

```python
# Get comprehensive health report
maintenance = MaintenanceAutomation(config)
health_report = maintenance.get_health_report()

print(f"System Healthy: {health_report['healthy']}")
print(f"Battery: {health_report['battery']['percentage']:.1f}%")
print(f"Sensors: {health_report['sensors']}")
print(f"System Resources: {health_report['system']}")
```

#### Real-time Monitoring

```bash
# View diagnostics in real-time
ros2 topic echo /diagnostics

# Monitor specific metrics
ros2 topic echo /battery_status
ros2 topic echo /scan
```

### Performance Monitoring

#### System Resources

```bash
# Monitor CPU and memory usage
htop

# Monitor ROS2 topics
ros2 topic hz /scan
ros2 topic bw /camera/image_raw
```

#### Detection Performance

```python
# Get detection statistics
stats = detector.get_detection_stats()
print(f"Detection FPS: {stats['current_fps']}")
print(f"Total Detections: {stats['total_detections']}")
print(f"Active: {stats['is_active']}")
```

### Logging

#### Log Files

The system generates comprehensive logs:

```bash
# View main log file
tail -f turtlebot_automation.log

# View module-specific logs
tail -f logs/maintenance.log
tail -f logs/navigation.log
tail -f logs/detection.log
```

#### Log Levels

Configure logging verbosity:

```yaml
# config/automation_config.yaml
maintenance:
  log_level: "INFO"  # DEBUG, INFO, WARNING, ERROR

system:
  log_file: "turtlebot_automation.log"
```

## Configuration

### Main Configuration

Edit `config/automation_config.yaml`:

```yaml
# Simulation Settings
simulation:
  world_name: "turtlebot3_world"
  robot_model: "waffle"  # burger, waffle, waffle_pi
  headless: false
  use_rviz: true

# Navigation Settings
navigation:
  use_slam: true
  localization: false
  update_frequency: 10.0
  controller_frequency: 20.0

# Object Detection Settings
detection:
  model_path: "yolov8n.pt"
  confidence: 0.5
  camera_topic: "/camera/image_raw"
  max_detections: 100

# Voice Control Settings
voice:
  recognition_engine: "google"
  tts_engine: "gtts"
  wake_word: "turtlebot"
  language: "en-US"

# Maintenance Settings
maintenance:
  health_check_interval: 30.0
  battery_threshold: 20.0
  log_level: "INFO"
```

### Location Configuration

Add custom navigation locations:

```yaml
# Add to config/automation_config.yaml
locations:
  kitchen: [3.0, 2.0, 0.0]
  living_room: [1.0, 1.0, 1.57]
  bedroom: [2.0, 3.0, -1.57]
  office: [4.0, 1.0, 1.57]
  entrance: [0.0, 0.0, 0.0]
  home: [0.0, 0.0, 0.0]
```

### Environment Variables

Set system-wide configuration:

```bash
# Add to ~/.bashrc
export TURTLEBOT3_MODEL=waffle
export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:/opt/ros/humble/share/turtlebot3_gazebo/models
export ROS_DOMAIN_ID=0
```

## Advanced Features

### Multi-Robot Support

Configure multiple robots:

```yaml
# config/multi_robot_config.yaml
system:
  robot_id: "robot_1"
  ros_domain_id: 1
  
navigation:
  robot_namespace: "robot_1"
  map_frame: "robot_1/map"
  
voice:
  wake_word: "robot one"
```

### Custom Worlds

Create custom simulation worlds:

```bash
# Launch with custom world
ros2 launch turtlebot_automation full_automation.launch.py \
    world_name:=my_custom_world \
    x_pose:=2.0 \
    y_pose:=1.0 \
    yaw:=1.57
```

### Integration with External Systems

#### Web Interface

```python
# Example web integration
from flask import Flask, jsonify
from modules.navigation_automation import NavigationAutomation

app = Flask(__name__)
nav = NavigationAutomation(config)

@app.route('/navigate', methods=['POST'])
def navigate():
    data = request.json
    success = nav.navigate_to_pose(data['x'], data['y'], data.get('yaw', 0))
    return jsonify({'success': success})

@app.route('/status')
def status():
    return jsonify(nav.get_navigation_status())
```

#### Mobile App Integration

```python
# Example mobile app API
@app.route('/voice_command', methods=['POST'])
def voice_command():
    command = request.json['command']
    # Process voice command
    voice._process_voice_command(command)
    return jsonify({'status': 'processed'})
```

### Performance Optimization

#### GPU Acceleration

```yaml
# Enable GPU for object detection
detection:
  device: "cuda"  # or "cpu"
  batch_size: 1
  workers: 4
```

#### Resource Management

```yaml
# Optimize system resources
maintenance:
  health_check_interval: 60.0  # Reduce frequency
  enable_diagnostics: false   # Disable if not needed
  
navigation:
  update_frequency: 5.0      # Reduce update rate
  controller_frequency: 10.0
```

## Troubleshooting

### Common Issues

#### System Won't Start

**Problem**: System fails to initialize

**Solution**:
```bash
# Check ROS2 environment
source /opt/ros/humble/setup.bash
ros2 topic list

# Check dependencies
python -c "import rclpy, cv2, torch; print('Dependencies OK')"

# Check configuration
python -c "import yaml; print(yaml.safe_load(open('config/automation_config.yaml')))"
```

#### Navigation Not Working

**Problem**: Robot doesn't move or navigate

**Solution**:
```bash
# Check navigation stack
ros2 node list | grep nav2

# Check map
ros2 topic echo /map --once

# Check odometry
ros2 topic echo /odom --once
```

#### Object Detection Not Working

**Problem**: No object detections

**Solution**:
```bash
# Check camera feed
ros2 topic echo /camera/image_raw --once

# Check detection topic
ros2 topic echo /object_detections --once

# Test detection manually
python modules/object_detection.py --test-image test.jpg
```

#### Voice Control Not Working

**Problem**: Voice commands not recognized

**Solution**:
```bash
# Test microphone
python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"

# Test voice recognition
python -c "
import speech_recognition as sr
r = sr.Recognizer()
with sr.Microphone() as source:
    print('Speak...')
    audio = r.listen(source)
    print('You said:', r.recognize_google(audio))
"
```

### Performance Issues

#### High CPU Usage

**Problem**: System using excessive CPU

**Solution**:
```yaml
# Reduce update frequencies
navigation:
  update_frequency: 5.0
  controller_frequency: 10.0

maintenance:
  health_check_interval: 60.0
```

#### Low Detection FPS

**Problem**: Object detection running slowly

**Solution**:
```yaml
# Optimize detection settings
detection:
  model_path: "yolov8n.pt"  # Use smaller model
  confidence: 0.6              # Increase threshold
  device: "cuda"               # Use GPU if available
```

### Getting Help

#### Debug Mode

```bash
# Enable verbose logging
python turtlebot_automation.py --verbose

# Check log files
tail -f turtlebot_automation.log
```

#### System Diagnostics

```bash
# Run system health check
python turtlebot_automation.py --module maintenance

# Check all ROS2 nodes
ros2 node list

# Check all topics
ros2 topic list
```

#### Community Support

- **GitHub Issues**: Report bugs and request features
- **Documentation**: Check `docs/` directory for detailed guides
- **Examples**: See `docs/examples.md` for practical use cases

This user manual provides comprehensive coverage of all system features. For additional help, refer to the API reference and troubleshooting guides.
# Troubleshooting Guide

This comprehensive troubleshooting guide addresses common issues and provides solutions for the TurtleBot3 automation system.

## Table of Contents

- [Installation Issues](#installation-issues)
- [ROS2 Problems](#ros2-problems)
- [Simulation Issues](#simulation-issues)
- [Navigation Problems](#navigation-problems)
- [Object Detection Issues](#object-detection-issues)
- [Voice Control Problems](#voice-control-problems)
- [Performance Issues](#performance-issues)
- [System Monitoring](#system-monitoring)
- [Debugging Tools](#debugging-tools)

## Installation Issues

### ROS2 Not Found

**Problem**: `bash: ros2: command not found`

**Symptoms**:
- Cannot run `ros2` commands
- Import errors for ROS2 packages

**Solutions**:

1. **Check ROS2 Installation**:
   ```bash
   # Check if ROS2 is installed
   ls /opt/ros/
   
   # Should see: foxy, galactic, humble, etc.
   ```

2. **Source ROS2 Environment**:
   ```bash
   # For Ubuntu 22.04 (Humble)
   source /opt/ros/humble/setup.bash
   
   # For Ubuntu 20.04 (Foxy)
   source /opt/ros/foxy/setup.bash
   ```

3. **Add to Bashrc**:
   ```bash
   echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
   source ~/.bashrc
   ```

4. **Reinstall ROS2** (if needed):
   ```bash
   sudo apt update
   sudo apt install ros-humble-desktop
   ```

### Python Dependencies Missing

**Problem**: `ModuleNotFoundError` for Python packages

**Symptoms**:
- Import errors for rclpy, cv2, torch, etc.
- Pip installation failures

**Solutions**:

1. **Check Python Version**:
   ```bash
   python3 --version
   # Should be 3.8 or higher
   ```

2. **Install Dependencies**:
   ```bash
   # Install from requirements
   pip install -r requirements.txt
   
   # Or install individually
   pip install rclpy opencv-python torch ultralytics
   ```

3. **Check Python Path**:
   ```bash
   python3 -c "import sys; print(sys.path)"
   ```

4. **Virtual Environment** (recommended):
   ```bash
   python3 -m venv turtlebot_env
   source turtlebot_env/bin/activate
   pip install -r requirements.txt
   ```

### TurtleBot3 Packages Missing

**Problem**: Cannot find TurtleBot3 packages

**Symptoms**:
- `ros2 run turtlebot3_gazebo` fails
- Package not found errors

**Solutions**:

1. **Install TurtleBot3 Packages**:
   ```bash
   # For ROS2 Humble
   sudo apt install ros-humble-turtlebot3*
   
   # For ROS2 Foxy
   sudo apt install ros-foxy-turtlebot3*
   ```

2. **Check Installation**:
   ```bash
   ros2 pkg list | grep turtlebot3
   ```

3. **Set Environment Variables**:
   ```bash
   export TURTLEBOT3_MODEL=waffle
   echo "export TURTLEBOT3_MODEL=waffle" >> ~/.bashrc
   ```

## ROS2 Problems

### ROS2 Context Issues

**Problem**: ROS2 commands fail with context errors

**Symptoms**:
- `ros2 context list` shows no contexts
- Cannot create ROS2 nodes

**Solutions**:

1. **Check ROS2 Context**:
   ```bash
   ros2 context list
   ros2 context current
   ```

2. **Create Default Context**:
   ```bash
   ros2 context create default
   ros2 context set default
   ```

3. **Check Domain ID**:
   ```bash
   export ROS_DOMAIN_ID=0
   ```

### Node Registration Issues

**Problem**: Nodes cannot register or communicate

**Symptoms**:
- Nodes start but don't appear in `ros2 node list`
- Communication timeouts

**Solutions**:

1. **Check Network Configuration**:
   ```bash
   # Check ROS_DOMAIN_ID
   echo $ROS_DOMAIN_ID
   
   # All nodes must use same domain ID
   ```

2. **Check Firewall**:
   ```bash
   # Allow ROS2 communication
   sudo ufw allow 11311
   sudo ufw allow from 192.168.0.0/16
   ```

3. **Restart ROS2 Daemon**:
   ```bash
   pkill -f ros2
   ros2 daemon start
   ```

### Topic Communication Issues

**Problem**: Topics not publishing/subscribing

**Symptoms**:
- `ros2 topic echo` shows no data
- Nodes cannot see each other's topics

**Solutions**:

1. **Check Topic List**:
   ```bash
   ros2 topic list
   ros2 topic info /topic_name
   ```

2. **Check QoS Settings**:
   ```bash
   # Check topic QoS
   ros2 topic info /topic_name --verbose
   ```

3. **Verify Message Types**:
   ```bash
   ros2 interface show sensor_msgs/msg/LaserScan
   ```

## Simulation Issues

### Gazebo Won't Start

**Problem**: Gazebo fails to launch or crashes

**Symptoms**:
- Gazebo window doesn't appear
- Simulation crashes immediately
- Model loading errors

**Solutions**:

1. **Check Gazebo Installation**:
   ```bash
   gazebo --version
   sudo apt install gazebo
   ```

2. **Check Graphics Drivers**:
   ```bash
   glxinfo | grep "OpenGL renderer"
   nvidia-smi  # For NVIDIA GPUs
   ```

3. **Set Gazebo Model Path**:
   ```bash
   export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:/opt/ros/humble/share/turtlebot3_gazebo/models
   ```

4. **Run in Headless Mode** (for testing):
   ```bash
   export GAZEBO_RENDER_ENGINE=ogre
   gazebo --verbose -s libgazebo_ros_init.so
   ```

### TurtleBot3 Model Issues

**Problem**: TurtleBot3 model doesn't appear or is broken

**Symptoms**:
- Empty world in Gazebo
- Robot model missing parts
- Spawn errors

**Solutions**:

1. **Check Model Files**:
   ```bash
   ls /opt/ros/humble/share/turtlebot3_gazebo/models/
   ```

2. **Verify Robot Model**:
   ```bash
   echo $TURTLEBOT3_MODEL
   export TURTLEBOT3_MODEL=waffle  # or burger, waffle_pi
   ```

3. **Check World Files**:
   ```bash
   ls /opt/ros/humble/share/turtlebot3_gazebo/worlds/
   ```

4. **Manual Spawn**:
   ```bash
   ros2 service call /spawn_entity gazebo_msgs/srv/SpawnEntity \
     "{name: 'turtlebot3', xml: '', robot_namespace: '', initial_pose: {position: {x: 0.0, y: 0.0, z: 0.0}, orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}}}"
   ```

## Navigation Problems

### Navigation Stack Not Starting

**Problem**: Nav2 stack fails to initialize

**Symptoms**:
- Navigation action servers not available
- Costmap errors
- Path planning failures

**Solutions**:

1. **Check Nav2 Installation**:
   ```bash
   ros2 pkg list | grep nav2
   ```

2. **Check Navigation Nodes**:
   ```bash
   ros2 node list | grep nav2
   ```

3. **Verify Map**:
   ```bash
   ros2 topic echo /map --once
   ```

4. **Check Transform Tree**:
   ```bash
   ros2 run tf2_tools tf2_echo map base_link
   ```

### Path Planning Issues

**Problem**: Robot cannot plan paths to goals

**Symptoms**:
- Navigation goals rejected
- No valid paths found
- Robot stuck in local minima

**Solutions**:

1. **Check Costmap**:
   ```bash
   ros2 topic echo /local_costmap/costmap --once
   ros2 topic echo /global_costmap/costmap --once
   ```

2. **Adjust Costmap Parameters**:
   ```yaml
   # In nav2_params.yaml
   local_costmap:
     inflation_radius: 0.55
     cost_scaling_factor: 10.0
   global_costmap:
     inflation_radius: 0.55
     cost_scaling_factor: 10.0
   ```

3. **Check Robot Pose**:
   ```bash
   ros2 topic echo /amcl_pose --once
   ```

### Localization Issues

**Problem**: Robot cannot localize itself

**Symptoms**:
- AMCL fails to converge
- Particle filter issues
- Position jumps

**Solutions**:

1. **Check Initial Pose**:
   ```bash
   # Set initial pose in RViz
   # Or via command
   ros2 topic pub /initialpose geometry_msgs/msg/PoseWithCovarianceStamped \
     "header: {stamp: {sec: 0}, frame_id: 'map'}, \
      pose: {pose: {position: {x: 0.0, y: 0.0, z: 0.0}, \
                orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}}, \
               covariance: [0.0]*36}"
   ```

2. **Check Laser Scan**:
   ```bash
   ros2 topic echo /scan --once
   ```

3. **Adjust AMCL Parameters**:
   ```yaml
   amcl:
     min_particles: 100
     max_particles: 5000
     initial_pose_x: 0.0
     initial_pose_y: 0.0
     initial_pose_a: 0.0
   ```

## Object Detection Issues

### Camera Not Working

**Problem**: No camera feed or camera errors

**Symptoms**:
- `/camera/image_raw` topic has no data
- Camera device not found
- Image format errors

**Solutions**:

1. **Check Camera Topics**:
   ```bash
   ros2 topic list | grep camera
   ros2 topic hz /camera/image_raw
   ```

2. **Check Gazebo Camera**:
   ```bash
   # For simulation
   ros2 run ros_gz_image image_bridge /camera/image_raw
   ```

3. **Check Camera Device** (hardware):
   ```bash
   ls /dev/video*
   v4l2-ctl --list-devices
   ```

4. **Test Camera Feed**:
   ```bash
   # View camera feed
   ros2 run rqt_image_view rqt_image_view
   ```

### YOLOv8 Model Issues

**Problem**: Object detection fails or poor performance

**Symptoms**:
- Model loading errors
- No detections
- Very slow inference

**Solutions**:

1. **Check Model File**:
   ```bash
   ls -la yolov8n.pt
   # Model should download automatically on first run
   ```

2. **Test Model Manually**:
   ```python
   from ultralytics import YOLO
   model = YOLO('yolov8n.pt')
   results = model('test.jpg')
   print(f"Detected {len(results)} objects")
   ```

3. **Check GPU Support**:
   ```python
   import torch
   print(f"CUDA available: {torch.cuda.is_available()}")
   if torch.cuda.is_available():
       print(f"GPU: {torch.cuda.get_device_name()}")
   ```

4. **Optimize Performance**:
   ```yaml
   detection:
     model_path: "yolov8n.pt"  # Use smaller model
     confidence: 0.6              # Higher threshold
     device: "cuda"               # Use GPU if available
   ```

### Detection Accuracy Issues

**Problem**: Poor detection accuracy or false positives

**Symptoms**:
- Missing obvious objects
- False detections
- Low confidence scores

**Solutions**:

1. **Adjust Confidence Threshold**:
   ```yaml
   detection:
     confidence: 0.5  # Lower for more detections
     # confidence: 0.7  # Higher for fewer false positives
   ```

2. **Check Image Quality**:
   ```bash
   # View camera feed quality
   ros2 run rqt_image_view rqt_image_view
   ```

3. **Test Different Models**:
   ```yaml
   detection:
     model_path: "yolov8s.pt"  # Better accuracy, slower
     # model_path: "yolov8n.pt"  # Faster, less accurate
   ```

## Voice Control Problems

### Microphone Issues

**Problem**: Voice control cannot hear or process audio

**Symptoms**:
- Microphone not found
- Permission denied errors
- No audio input

**Solutions**:

1. **List Available Microphones**:
   ```python
   import speech_recognition as sr
   r = sr.Recognizer()
   print(sr.Microphone.list_microphone_names())
   ```

2. **Check Microphone Permissions**:
   ```bash
   # Add user to audio group
   sudo usermod -a -G audio $USER
   
   # Check microphone device
   ls -l /dev/snd/
   ```

3. **Test Microphone**:
   ```python
   import speech_recognition as sr
   r = sr.Recognizer()
   with sr.Microphone() as source:
       print("Say something!")
       audio = r.listen(source)
       print("You said: " + r.recognize_google(audio))
   ```

4. **Adjust Microphone Index**:
   ```yaml
   voice:
     microphone_index: 1  # Use specific microphone
   ```

### Speech Recognition Issues

**Problem**: Voice commands not recognized correctly

**Symptoms**:
- "Could not understand audio" errors
- Wrong command recognition
- Background noise interference

**Solutions**:

1. **Adjust for Ambient Noise**:
   ```python
   # In voice_control.py
   with self.microphone as source:
       self.recognizer.adjust_for_ambient_noise(source, duration=2)
   ```

2. **Use Different Recognition Engine**:
   ```yaml
   voice:
     recognition_engine: "sphinx"  # Offline, less accurate
     # recognition_engine: "google"  # Online, more accurate
   ```

3. **Improve Audio Quality**:
   ```bash
   # Use better microphone
   # Reduce background noise
   # Speak clearly and close to microphone
   ```

4. **Test Recognition**:
   ```python
   import speech_recognition as sr
   r = sr.Recognizer()
   
   # Test different engines
   try:
       text = r.recognize_google(audio)
   except:
       text = r.recognize_sphinx(audio)
   ```

### Text-to-Speech Issues

**Problem**: Voice feedback not working

**Symptoms**:
- No audio feedback
- TTS errors
- Audio playback issues

**Solutions**:

1. **Check TTS Installation**:
   ```bash
   pip install gtts playsound
   ```

2. **Test TTS**:
   ```python
   from gtts import gTTS
   import playsound
   
   tts = gTTS("Hello world", lang='en')
   tts.save("test.mp3")
   playsound("test.mp3")
   ```

3. **Check Audio System**:
   ```bash
   # Test audio playback
   aplay /usr/share/sounds/alsa/Front_Left.wav
   ```

4. **Use Alternative TTS**:
   ```yaml
   voice:
     tts_engine: "espeak"  # Alternative TTS engine
   ```

## Performance Issues

### High CPU Usage

**Problem**: System using excessive CPU resources

**Symptoms**:
- System running hot
- Poor performance
- High CPU usage in htop

**Solutions**:

1. **Monitor Resource Usage**:
   ```bash
   htop
   iotop
   ```

2. **Reduce Update Frequencies**:
   ```yaml
   navigation:
     update_frequency: 5.0      # Reduce from 10.0
     controller_frequency: 10.0  # Reduce from 20.0
   
   maintenance:
     health_check_interval: 60.0  # Reduce from 30.0
   ```

3. **Optimize Detection**:
   ```yaml
   detection:
     max_detections: 50         # Reduce from 100
     confidence: 0.7            # Increase threshold
   ```

4. **Use GPU Acceleration**:
   ```yaml
   detection:
     device: "cuda"  # Use GPU instead of CPU
   ```

### Memory Issues

**Problem**: System running out of memory

**Symptoms**:
- Out of memory errors
- System crashes
- Poor performance

**Solutions**:

1. **Monitor Memory Usage**:
   ```bash
   free -h
   ps aux --sort=-%mem | head
   ```

2. **Reduce Model Sizes**:
   ```yaml
   detection:
     model_path: "yolov8n.pt"  # Smaller model
   ```

3. **Limit Concurrent Processes**:
   ```yaml
   system:
     max_workers: 2  # Limit parallel processing
   ```

4. **Enable Memory Optimization**:
   ```python
   # In object detection
   torch.cuda.empty_cache()  # Clear GPU cache
   ```

### Network Issues

**Problem**: ROS2 communication problems

**Symptoms**:
- Nodes cannot communicate
- Topic delays
- Connection timeouts

**Solutions**:

1. **Check Network Configuration**:
   ```bash
   ip addr show
   ping localhost
   ```

2. **Check ROS2 Domain**:
   ```bash
   echo $ROS_DOMAIN_ID
   # All nodes must use same domain
   ```

3. **Disable Firewall**:
   ```bash
   sudo ufw disable
   # Or allow ROS2 ports
   sudo ufw allow 11311
   ```

4. **Use Localhost**:
   ```bash
   export ROS_LOCALHOST_ONLY=1
   ```

## System Monitoring

### Health Check Failures

**Problem**: System health checks failing

**Symptoms**:
- Health monitoring reports errors
- Sensor failures
- Battery warnings

**Solutions**:

1. **Check Health Report**:
   ```python
   from modules.maintenance_automation import MaintenanceAutomation
   
   maintenance = MaintenanceAutomation(config)
   report = maintenance.get_health_report()
   print(report)
   ```

2. **Check Individual Sensors**:
   ```bash
   ros2 topic echo /battery_status --once
   ros2 topic echo /scan --once
   ros2 topic echo /imu --once
   ```

3. **Adjust Health Thresholds**:
   ```yaml
   maintenance:
     battery_threshold: 15.0  # Lower threshold
     health_check_interval: 60.0  # Reduce frequency
   ```

### Diagnostic Errors

**Problem**: Diagnostic messages showing errors

**Symptoms**:
- Error status in diagnostics
- Warning messages
- Component failures

**Solutions**:

1. **Check Diagnostic Topics**:
   ```bash
   ros2 topic echo /diagnostics --once
   ```

2. **Check Individual Components**:
   ```bash
   ros2 node list
   ros2 topic list | grep diagnostic
   ```

3. **Reset Components**:
   ```bash
   # Restart failing nodes
   ros2 lifecycle set /component_name configure
   ros2 lifecycle set /component_name activate
   ```

## Debugging Tools

### Logging

**Enable Debug Logging**:
```bash
# Enable verbose logging
python turtlebot_automation.py --verbose

# Check log files
tail -f turtlebot_automation.log
tail -f logs/maintenance.log
```

**Log Levels**:
```yaml
maintenance:
  log_level: "DEBUG"  # DEBUG, INFO, WARNING, ERROR
```

### ROS2 Debugging

**Check ROS2 System**:
```bash
# Check nodes
ros2 node list

# Check topics
ros2 topic list

# Check services
ros2 service list

# Check actions
ros2 action list
```

**Monitor Topics**:
```bash
# Monitor topic frequency
ros2 topic hz /scan

# Monitor topic bandwidth
ros2 topic bw /camera/image_raw

# View topic data
ros2 topic echo /topic_name
```

### Performance Profiling

**Profile Python Code**:
```python
import cProfile
import pstats

# Profile object detection
cProfile.run('detector.detect_objects_sync("test.jpg")', 'profile_stats')
stats = pstats.Stats('profile_stats')
stats.sort_stats('cumulative')
stats.print_stats(10)
```

**Monitor System Resources**:
```bash
# CPU and memory
htop
iotop

# GPU usage (if available)
nvidia-smi

# Disk usage
df -h
```

### Network Debugging

**Check ROS2 Communication**:
```bash
# Check network interfaces
ip addr show

# Check ROS2 traffic
wireshark  # Filter for ROS2 ports

# Test connectivity
ros2 run demo_nodes_py talker
ros2 run demo_nodes_py listener
```

## Getting Help

### Collect Debug Information

When reporting issues, collect this information:

```bash
# System information
uname -a
lsb_release -a

# ROS2 information
ros2 --version
echo $ROS_DISTRO

# Python information
python3 --version
pip list | grep -E "(rclpy|opencv|torch|ultralytics)"

# Hardware information
lscpu
free -h
lspci | grep -i vga

# Error logs
journalctl -u ros2 -f
tail -50 turtlebot_automation.log
```

### Issue Report Template

```markdown
## Environment
- OS: [Ubuntu version]
- ROS2: [Humble/Foxy]
- Python: [3.x.x]
- Hardware: [CPU/RAM/GPU]

## Problem Description
[Detailed description of the issue]

## Steps to Reproduce
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Error Messages
```
[Paste full error output]
```

## What You Tried
[Include troubleshooting steps attempted]

## Additional Information
[Any other relevant information]
```

### Community Resources

- **GitHub Issues**: Report bugs and request features
- **Documentation**: Check `docs/` directory
- **Forums**: ROS2 and TurtleBot3 community forums
- **Discord/Slack**: Real-time chat support

This troubleshooting guide should help resolve most common issues. For persistent problems, collect debug information and seek community support.
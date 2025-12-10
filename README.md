# TurtleBot3 Comprehensive Automation System

A complete automation solution for TurtleBot3 that integrates setup, maintenance, navigation, object detection, and voice control capabilities. This project is designed for both simulation and hardware deployment, providing a modular architecture that can be easily extended and customized.

## 🚀 Features

### Core Automation Modules

1. **Setup Automation** - Automated ROS2 and TurtleBot3 installation and configuration
2. **Maintenance Automation** - Real-time health monitoring, diagnostics, and system maintenance
3. **Navigation Automation** - SLAM, path planning, and autonomous navigation using Nav2
4. **Object Detection** - YOLOv8-based object detection with OpenCV integration
5. **Voice Control** - Custom voice command system for robot control (Custom Feature)

### Key Capabilities

- **Simulation Ready**: Full Gazebo simulation support with virtual environments
- **Hardware Compatible**: Works with real TurtleBot3 hardware
- **Modular Design**: Each component can run independently or as part of the full system
- **AI Integration**: Modern AI tools for object detection and voice recognition
- **Health Monitoring**: Comprehensive system diagnostics and maintenance alerts
- **Autonomous Navigation**: SLAM mapping and waypoint navigation
- **Real-time Detection**: Live object detection with ROS2 topic integration
- **Voice Commands**: Natural language control of robot functions

## 📋 Prerequisites

### System Requirements

- **Operating System**: Ubuntu 20.04+ (for ROS2 Humble) or Ubuntu 18.04+ (for ROS2 Foxy)
- **Python**: 3.8 or higher
- **ROS2**: Humble (recommended) or Foxy
- **Hardware**: TurtleBot3 Burger/Waffle/Waffle Pi (optional for simulation)
- **Memory**: Minimum 4GB RAM, 8GB recommended
- **Storage**: 10GB free space for dependencies and models

### Software Dependencies

See `requirements.txt` for complete Python dependencies. Key packages include:

```bash
# Core ROS2 packages (installed via setup automation)
ros-humble-desktop
ros-humble-navigation2
ros-humble-turtlebot3*

# Python packages
pip install -r requirements.txt
```

## 🛠️ Installation

### Quick Start (Simulation)

```bash
# Clone the repository
git clone https://github.com/asadbey/turtlebot-automation.git
cd turtlebot-automation

# Install Python dependencies
pip install -r requirements.txt

# Run automated setup (installs ROS2 and TurtleBot3 packages)
python turtlebot_automation.py --module setup

# Launch full automation system
python turtlebot_automation.py
```

### Manual Installation

1. **Install ROS2** (if not already installed):
```bash
# Follow official ROS2 installation guide for your Ubuntu version
# https://docs.ros.org/en/rolling/Installation.html
```

2. **Install TurtleBot3 Packages**:
```bash
sudo apt update
sudo apt install ros-humble-turtlebot3* ros-humble-navigation2
```

3. **Setup Python Environment**:
```bash
pip install -r requirements.txt
```

4. **Build ROS Workspace**:
```bash
cd ~/turtlebot3_ws
colcon build
source install/setup.bash
```

## 🚀 Usage

### Running the Full System

```bash
# Run complete automation system in simulation mode
python turtlebot_automation.py

# Run with hardware (disable simulation)
python turtlebot_automation.py --no-simulation

# Run with custom configuration
python turtlebot_automation.py --config config/my_config.yaml

# Enable verbose logging
python turtlebot_automation.py --verbose
```

### Running Individual Modules

```bash
# Run setup automation only
python turtlebot_automation.py --module setup

# Run maintenance monitoring
python turtlebot_automation.py --module maintenance

# Run navigation system
python turtlebot_automation.py --module navigation

# Run object detection
python turtlebot_automation.py --module detection

# Run voice control
python turtlebot_automation.py --module voice
```

### Using ROS2 Launch Files

```bash
# Launch complete automation system
ros2 launch turtlebot_automation full_automation.launch.py

# Launch with custom parameters
ros2 launch turtlebot_automation full_automation.launch.py \
    robot_model:=waffle \
    use_rviz:=true \
    headless:=false
```

## 🎮 Voice Commands

The voice control system supports natural language commands:

### Movement Commands
- "TurtleBot move forward"
- "TurtleBot turn left"
- "TurtleBot stop"
- "TurtleBot emergency stop"

### Navigation Commands
- "TurtleBot navigate to kitchen"
- "TurtleBot go to living room"
- "TurtleBot explore"

### Information Commands
- "TurtleBot what do you see?"
- "TurtleBot scan for objects"

### Special Commands
- "TurtleBot follow me"
- "TurtleBot stop following"

## 🔧 Configuration

### Main Configuration

Edit `config/automation_config.yaml` to customize system behavior:

```yaml
# Simulation Settings
simulation:
  world_name: "turtlebot3_world"
  robot_model: "waffle"
  headless: false
  use_rviz: true

# Object Detection Settings
detection:
  model_path: "yolov8n.pt"
  confidence: 0.5
  camera_topic: "/camera/image_raw"

# Voice Control Settings
voice:
  recognition_engine: "google"
  wake_word: "turtlebot"
  language: "en-US"
```

### Navigation Locations

Add custom navigation locations in the configuration:

```yaml
locations:
  kitchen: [3.0, 2.0, 0.0]
  bedroom: [2.0, 3.0, -1.57]
  office: [4.0, 1.0, 1.57]
```

## 📊 System Architecture

### Module Structure

```
turtlebot-automation/
├── turtlebot_automation.py          # Main automation orchestrator
├── modules/                          # Core automation modules
│   ├── setup_automation.py          # Setup and installation
│   ├── maintenance_automation.py    # Health monitoring
│   ├── navigation_automation.py     # SLAM and navigation
│   ├── object_detection.py          # YOLOv8 detection
│   └── voice_control.py             # Voice commands
├── config/                           # Configuration files
├── launch/                           # ROS2 launch files
├── scripts/                          # Utility scripts
└── tests/                            # Unit tests
```

### Data Flow

1. **Setup Module** → Configures ROS2 environment and dependencies
2. **Maintenance Module** → Monitors system health and publishes diagnostics
3. **Navigation Module** → Handles SLAM, path planning, and robot movement
4. **Detection Module** → Processes camera images and publishes object detections
5. **Voice Module** → Listens for commands and controls robot behavior

### ROS2 Topics

Key topics used by the system:

- `/cmd_vel` - Robot velocity commands
- `/camera/image_raw` - Camera feed for object detection
- `/object_detections` - Detection results
- `/voice_commands` - Voice command data
- `/diagnostics` - System health information
- `/map` - Occupancy grid map
- `/scan` - LIDAR scan data

## 🧪 Testing

### Unit Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_navigation.py

# Run with coverage
python -m pytest --cov=modules tests/
```

### Integration Tests

```bash
# Test individual modules
python -m modules.setup_automation
python -m modules.object_detection

# Test with sample data
python modules/object_detection.py --test-image test/sample.jpg
```

## 📹 Demo Video

A comprehensive demonstration video is available showing:

- System setup and installation
- Simulation environment launch
- Autonomous navigation with SLAM
- Real-time object detection
- Voice command control
- Health monitoring and diagnostics

[Link to Demo Video]

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add unit tests for new features
- Update documentation for API changes
- Use meaningful commit messages

## 📝 API Reference

### Main Automation Class

```python
from turtlebot_automation import TurtleBotAutomation

# Create automation instance
automation = TurtleBotAutomation(
    config_file="config/my_config.yaml",
    simulation_mode=True
)

# Run full system
automation.run_full_automation()

# Run individual module
automation.run_individual_module("navigation")
```

### Module APIs

Each module can be used independently:

```python
from modules.navigation_automation import NavigationAutomation
from modules.object_detection import ObjectDetection

# Navigation
nav = NavigationAutomation(config, simulation_mode=True)
nav.navigate_to_pose(2.0, 3.0, 1.57)

# Object Detection
detector = ObjectDetection(config)
detections = detector.detect_objects_sync("image.jpg")
```

## 🐛 Troubleshooting

### Common Issues

1. **ROS2 Not Found**
   ```bash
   source /opt/ros/humble/setup.bash
   ```

2. **TurtleBot3 Model Not Set**
   ```bash
   export TURTLEBOT3_MODEL=waffle
   ```

3. **Gazebo Model Path Issues**
   ```bash
   export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:/opt/ros/humble/share/turtlebot3_gazebo/models
   ```

4. **Camera Not Working in Simulation**
   - Ensure `ros-gz-image` is installed
   - Check camera bridge is running: `ros2 run ros_gz_image image_bridge /camera/image_raw`

5. **Voice Recognition Not Working**
   - Check microphone permissions
   - Install audio dependencies: `sudo apt install portaudio19-dev`
   - Test with: `python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"`

### Debug Mode

Enable debug logging:

```bash
python turtlebot_automation.py --verbose
```

Check log files:

```bash
tail -f turtlebot_automation.log
```

## 📚 References

- [ROS2 Documentation](https://docs.ros.org/en/rolling/)
- [TurtleBot3 e-Manual](https://emanual.robotis.com/docs/en/platform/turtlebot3/)
- [Nav2 Navigation Stack](https://navigation.ros.org/)
- [YOLOv8 Documentation](https://docs.ultralytics.com/)
- [Gazebo Simulator](http://gazebosim.org/)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Robotis for TurtleBot3 platform
- Open Robotics for ROS2 and Gazebo
- Ultralytics for YOLOv8
- The ROS2 community for navigation and simulation tools

## 📞 Support

For support and questions:

- Create an issue on GitHub
- Check the troubleshooting section
- Review the API documentation
- Join our community discussions

---

**Note**: This project was developed as part of a comprehensive robotics automation assignment, demonstrating integration of modern AI tools with ROS2 robotics platforms.
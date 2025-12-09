# API Reference

This document provides detailed API documentation for all modules and classes in the TurtleBot3 automation system.

## Table of Contents

- [Main Automation Class](#main-automation-class)
- [Setup Automation](#setup-automation)
- [Maintenance Automation](#maintenance-automation)
- [Navigation Automation](#navigation-automation)
- [Object Detection](#object-detection)
- [Voice Control](#voice-control)

## Main Automation Class

### TurtleBotAutomation

Main orchestrator class that coordinates all automation modules.

#### Constructor

```python
TurtleBotAutomation(config_file: Optional[str] = None, simulation_mode: bool = True)
```

**Parameters:**
- `config_file` (str, optional): Path to YAML configuration file
- `simulation_mode` (bool): True for simulation, False for hardware

**Returns:**
- `TurtleBotAutomation` instance

#### Methods

##### initialize_ros()

Initialize ROS2 context and nodes.

```python
initialize_ros() -> bool
```

**Returns:**
- `bool`: True if successful, False otherwise

##### initialize_modules()

Initialize all automation modules.

```python
initialize_modules() -> bool
```

**Returns:**
- `bool`: True if all modules initialized successfully

##### run_full_automation()

Execute complete automation pipeline.

```python
run_full_automation() -> None
```

##### run_individual_module()

Run specific automation module.

```python
run_individual_module(module_name: str) -> None
```

**Parameters:**
- `module_name` (str): Name of module to run ('setup', 'maintenance', 'navigation', 'detection', 'voice')

##### shutdown()

Graceful shutdown of all systems.

```python
shutdown() -> None
```

#### Usage Example

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

## Setup Automation

### SetupAutomation

Handles ROS2 and TurtleBot3 installation and configuration.

#### Constructor

```python
SetupAutomation(config: Dict, simulation_mode: bool = True)
```

**Parameters:**
- `config` (Dict): Configuration dictionary
- `simulation_mode` (bool): True for simulation setup

#### Methods

##### initialize()

Initialize setup module.

```python
initialize() -> bool
```

##### needs_setup()

Check if setup is needed.

```python
needs_setup() -> bool
```

##### run_setup()

Run complete setup process.

```python
run_setup() -> bool
```

##### get_workspace_path()

Get ROS workspace path.

```python
get_workspace_path() -> Path
```

##### get_ros_distro()

Get ROS2 distribution.

```python
get_ros_distro() -> str
```

#### Usage Example

```python
from modules.setup_automation import SetupAutomation

config = {"simulation": {"robot_model": "waffle"}}
setup = SetupAutomation(config, simulation_mode=True)

if setup.needs_setup():
    setup.run_setup()
```

## Maintenance Automation

### MaintenanceAutomation

Monitors system health, battery status, and sensor diagnostics.

#### Constructor

```python
MaintenanceAutomation(config: Dict)
```

#### Methods

##### initialize()

Initialize maintenance module.

```python
initialize() -> bool
```

##### start_monitoring()

Start health monitoring loop.

```python
start_monitoring() -> None
```

##### stop_monitoring()

Stop health monitoring.

```python
stop_monitoring() -> None
```

##### is_healthy()

Check if overall system is healthy.

```python
is_healthy() -> bool
```

##### get_health_report()

Get comprehensive health report.

```python
get_health_report() -> Dict
```

**Returns:**
```python
{
    'timestamp': float,
    'healthy': bool,
    'battery': Dict,
    'sensors': Dict,
    'motors': Dict,
    'navigation': Dict,
    'system': Dict
}
```

#### Usage Example

```python
from modules.maintenance_automation import MaintenanceAutomation

maintenance = MaintenanceAutomation(config)
maintenance.initialize()
maintenance.start_monitoring()

# Check health
if not maintenance.is_healthy():
    report = maintenance.get_health_report()
    print(f"System unhealthy: {report}")
```

## Navigation Automation

### NavigationAutomation

Handles SLAM, path planning, and autonomous navigation.

#### Constructor

```python
NavigationAutomation(config: Dict, simulation_mode: bool = True)
```

#### Methods

##### initialize()

Initialize navigation module.

```python
initialize() -> bool
```

##### start_navigation()

Start navigation system.

```python
start_navigation() -> None
```

##### navigate_to_pose()

Navigate to specific pose.

```python
navigate_to_pose(x: float, y: float, yaw: float = 0.0) -> bool
```

**Parameters:**
- `x` (float): Target X coordinate
- `y` (float): Target Y coordinate  
- `yaw` (float): Target yaw angle in radians

**Returns:**
- `bool`: True if navigation started successfully

##### follow_waypoints()

Follow a series of waypoints.

```python
follow_waypoints(waypoints: List[Tuple[float, float, float]]) -> bool
```

**Parameters:**
- `waypoints`: List of (x, y, yaw) tuples

##### stop_robot()

Stop robot movement.

```python
stop_robot() -> None
```

##### set_initial_pose()

Set initial robot pose for localization.

```python
set_initial_pose(x: float, y: float, yaw: float) -> None
```

##### get_current_pose()

Get current robot pose.

```python
get_current_pose() -> Optional[PoseWithCovarianceStamped]
```

##### is_navigation_active()

Check if navigation is currently active.

```python
is_navigation_active() -> bool
```

#### Usage Example

```python
from modules.navigation_automation import NavigationAutomation

nav = NavigationAutomation(config, simulation_mode=True)
nav.initialize()
nav.start_navigation()

# Navigate to location
nav.navigate_to_pose(2.0, 3.0, 1.57)

# Follow waypoints
waypoints = [(1.0, 1.0, 0.0), (2.0, 2.0, 1.57), (3.0, 1.0, 0.0)]
nav.follow_waypoints(waypoints)
```

## Object Detection

### ObjectDetection

Handles YOLOv8 object detection with OpenCV integration.

#### Constructor

```python
ObjectDetection(config: Dict)
```

#### Methods

##### initialize()

Initialize object detection module.

```python
initialize() -> bool
```

##### start_detection()

Start object detection.

```python
start_detection() -> None
```

##### stop_detection()

Stop object detection.

```python
stop_detection() -> None
```

##### detect_objects_sync()

Synchronous object detection for testing.

```python
detect_objects_sync(image_path: str) -> List[Dict]
```

**Parameters:**
- `image_path` (str): Path to image file

**Returns:**
- `List[Dict]`: List of detection dictionaries

**Detection Dictionary Format:**
```python
{
    'bbox': [x1, y1, x2, y2],
    'confidence': float,
    'class_id': int,
    'class_name': str
}
```

##### get_detection_stats()

Get detection performance statistics.

```python
get_detection_stats() -> Dict
```

#### Usage Example

```python
from modules.object_detection import ObjectDetection

detector = ObjectDetection(config)
detector.initialize()
detector.start_detection()

# Synchronous detection
detections = detector.detect_objects_sync("test_image.jpg")
for detection in detections:
    print(f"Detected {detection['class_name']} with confidence {detection['confidence']}")
```

## Voice Control

### VoiceControl

Handles speech recognition and voice commands.

#### Constructor

```python
VoiceControl(config: Dict)
```

#### Methods

##### initialize()

Initialize voice control module.

```python
initialize() -> bool
```

##### start_voice_control()

Start voice control system.

```python
start_voice_control() -> None
```

##### stop_voice_control()

Stop voice control system.

```python
stop_voice_control() -> None
```

##### add_location()

Add a new navigation location.

```python
add_location(name: str, x: float, y: float, yaw: float) -> None
```

##### get_locations()

Get all navigation locations.

```python
get_locations() -> Dict[str, tuple]
```

##### is_listening_active()

Check if voice control is actively listening.

```python
is_listening_active() -> bool
```

##### speak()

Convert text to speech.

```python
speak(text: str) -> None
```

#### Supported Voice Commands

- **Movement**: "move forward", "turn left", "stop", "emergency stop"
- **Navigation**: "navigate to [location]", "go to [location]"
- **Information**: "what do you see?", "scan for objects"
- **Special**: "follow me", "explore"

#### Usage Example

```python
from modules.voice_control import VoiceControl

voice = VoiceControl(config)
voice.initialize()
voice.start_voice_control()

# Add custom location
voice.add_location("office", 4.0, 1.0, 1.57)

# Get all locations
locations = voice.get_locations()
print(f"Available locations: {list(locations.keys())}")
```

## Error Handling

All modules implement comprehensive error handling:

### Common Exceptions

- `ImportError`: Required dependencies not available
- `ConnectionError`: ROS2 connection issues
- `ValueError`: Invalid parameters or configuration
- `RuntimeError`: Runtime execution errors

### Error Recovery

- Automatic retry mechanisms for network operations
- Fallback modes when dependencies unavailable
- Graceful degradation of functionality
- Comprehensive logging for debugging

## Configuration

All modules accept configuration dictionaries with the following structure:

```yaml
simulation:
  world_name: "turtlebot3_world"
  robot_model: "waffle"
  headless: false
  use_rviz: true

navigation:
  use_slam: true
  localization: false
  update_frequency: 10.0

detection:
  model_path: "yolov8n.pt"
  confidence: 0.5
  camera_topic: "/camera/image_raw"

voice:
  recognition_engine: "google"
  tts_engine: "gtts"
  wake_word: "turtlebot"

maintenance:
  health_check_interval: 30.0
  battery_threshold: 20.0
```

## ROS2 Topics

### Published Topics

- `/object_detections` - Detection results (Detection2DArray)
- `/detection_image` - Annotated camera feed (Image)
- `/diagnostics` - System health information (DiagnosticArray)
- `/voice_commands` - Voice command data (String)

### Subscribed Topics

- `/camera/image_raw` - Camera feed (Image)
- `/scan` - LIDAR scan data (LaserScan)
- `/odom` - Odometry data (Odometry)
- `/battery_status` - Battery information (BatteryState)
- `/imu` - IMU data (Imu)

### Action Servers

- `/navigate_to_pose` - Navigation action (NavigateToPose)
- `/follow_waypoints` - Waypoint following (FollowWaypoints)
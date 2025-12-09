# Developer Guide

This comprehensive developer guide covers extending and contributing to the TurtleBot3 automation system.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Development Environment Setup](#development-environment-setup)
- [Code Structure](#code-structure)
- [Module Development](#module-development)
- [Adding New Features](#adding-new-features)
- [Testing Guidelines](#testing-guidelines)
- [Debugging Techniques](#debugging-techniques)
- [Performance Optimization](#performance-optimization)
- [Contribution Guidelines](#contribution-guidelines)

## Architecture Overview

### System Architecture

The TurtleBot3 automation system follows a modular architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                Main Automation Orchestrator          │
│                    turtlebot_automation.py          │
├─────────────────────────────────────────────────────────┤
│  Setup    │ Maintenance │ Navigation │ Detection │ Voice │
│ Automation │  Automation │  Automation │ Automation │ Control │
├─────────────────────────────────────────────────────────┤
│  ROS2     │   Health     │   SLAM &    │   YOLOv8   │ Speech   │
│  Install  │   Monitoring │   Nav2       │   OpenCV    │ Recognition│
└─────────────────────────────────────────────────────────┘
```

### Design Principles

1. **Modularity**: Each module is self-contained and can run independently
2. **Extensibility**: Easy to add new modules and features
3. **Configuration-Driven**: All behavior controlled through configuration files
4. **Error Handling**: Comprehensive error handling and fallback modes
5. **ROS2 Integration**: Native ROS2 support with simulation fallbacks

### Data Flow

```
Configuration → Main Orchestrator → Individual Modules → ROS2 Topics
     ↓                    ↓                      ↓              ↓
   YAML Files          Module APIs      rclpy Nodes     Gazebo/Webots
```

## Development Environment Setup

### Prerequisites

- **Python 3.8+**: Required for all development
- **ROS2 Humble/Foxy**: For testing with real robots
- **Git**: Version control and collaboration
- **VS Code/PyCharm**: Recommended IDEs
- **Docker**: Optional for containerized development

### Development Setup

1. **Clone Repository**:
   ```bash
   git clone https://github.com/yourusername/turtlebot-automation.git
   cd turtlebot-automation
   ```

2. **Create Virtual Environment**:
   ```bash
   python3 -m venv dev_env
   source dev_env/bin/activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

3. **Install Pre-commit Hooks**:
   ```bash
   pip install pre-commit
   pre-commit install
   ```

4. **Setup IDE Configuration**:
   - Configure Python interpreter
   - Install ROS2 extensions
   - Setup code formatting (Black, flake8)

### Development Dependencies

```bash
# Core development tools
pip install black flake8 pytest pytest-cov mypy

# ROS2 development
pip install rclpy nav2-simple-commander

# AI/ML development
pip install jupyterlab matplotlib seaborn

# Documentation
pip install sphinx sphinx-rtd-theme
```

## Code Structure

### Project Organization

```
turtlebot-automation/
├── turtlebot_automation.py          # Main orchestrator
├── modules/                          # Core modules
│   ├── __init__.py
│   ├── setup_automation.py
│   ├── maintenance_automation.py
│   ├── navigation_automation.py
│   ├── object_detection.py
│   └── voice_control.py
├── config/                           # Configuration files
│   ├── automation_config.yaml
│   ├── nav2_params.yaml
│   └── detection_params.yaml
├── launch/                           # ROS2 launch files
│   ├── full_automation.launch.py
│   ├── navigation_only.launch.py
│   └── detection_only.launch.py
├── scripts/                          # Utility scripts
│   ├── install_dependencies.sh
│   ├── setup_workspace.sh
│   └── run_tests.sh
├── tests/                            # Test suite
│   ├── test_setup.py
│   ├── test_navigation.py
│   ├── test_detection.py
│   └── test_voice.py
├── docs/                             # Documentation
│   ├── api_reference.md
│   ├── user_manual.md
│   ├── troubleshooting.md
│   └── examples.md
├── examples/                          # Example scripts
│   ├── basic_usage.py
│   ├── advanced_scenarios.py
│   └── custom_extensions.py
├── package.xml                        # ROS2 package configuration
├── requirements.txt                   # Python dependencies
└── README.md                          # Project documentation
```

### Module Template

```python
#!/usr/bin/env python3
"""
Module Template for TurtleBot3 Automation
"""

import rclpy
import logging
from typing import Dict, Optional

# ROS2 imports
try:
    from rclpy.node import Node
    from std_msgs.msg import String
except ImportError:
    Node = object
    String = object


class ModuleTemplate(Node if 'Node' in globals() else object):
    """Template for new automation modules"""
    
    def __init__(self, config: Dict):
        """Initialize module with configuration"""
        # Initialize ROS node if available
        if 'Node' in globals():
            super().__init__('module_template')
            
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Module state
        self.is_active = False
        
        # ROS2 components (will be initialized in initialize())
        self.publisher = None
        self.subscriber = None
        
    def initialize(self) -> bool:
        """Initialize module components"""
        try:
            self.logger.info("Initializing module template")
            
            if 'Node' in globals():
                self._setup_ros_connections()
            
            self.logger.info("Module template initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize module: {e}")
            return False
            
    def _setup_ros_connections(self) -> None:
        """Setup ROS2 publishers and subscribers"""
        if 'Node' in globals():
            self.publisher = self.create_publisher(String, '/module_output', 10)
            self.subscriber = self.create_subscription(
                String,
                '/module_input',
                self._callback,
                10
            )
            
    def _callback(self, msg: String) -> None:
        """Handle incoming messages"""
        self.logger.info(f"Received: {msg.data}")
        
    def start(self) -> None:
        """Start module operation"""
        self.is_active = True
        self.logger.info("Module template started")
        
    def stop(self) -> None:
        """Stop module operation"""
        self.is_active = False
        self.logger.info("Module template stopped")
        
    def run(self) -> None:
        """Run module (blocking)"""
        self.start()
        try:
            while rclpy.ok() and self.is_active:
                rclpy.spin_once(self, timeout_sec=1.0)
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        finally:
            self.stop()
            
    def shutdown(self) -> None:
        """Shutdown module and cleanup resources"""
        self.stop()
        
        if 'Node' in globals():
            self.destroy_node()
            
        self.logger.info("Module template shutdown complete")
```

## Module Development

### Creating a New Module

1. **Create Module File**:
   ```bash
   touch modules/new_module.py
   ```

2. **Implement Module Interface**:
   ```python
   # Follow the module template above
   # Implement required methods: initialize(), start(), stop(), shutdown()
   # Add module-specific functionality
   ```

3. **Add Configuration**:
   ```yaml
   # config/automation_config.yaml
   new_module:
     enabled: true
     parameter1: value1
     parameter2: value2
   ```

4. **Update Main Orchestrator**:
   ```python
   # In turtlebot_automation.py
   from modules.new_module import NewModule
   
   # Add to modules dict
   self.modules['new_module'] = NewModule(self.config)
   ```

### Module Integration Points

#### ROS2 Integration

```python
# Publishers
self.detection_pub = self.create_publisher(
    Detection2DArray,
    '/object_detections',
    10
)

# Subscribers
self.image_sub = self.create_subscription(
    Image,
    '/camera/image_raw',
    self._image_callback,
    10
)

# Services
self.service_client = self.create_client(
    Trigger,
    '/trigger_service'
)

# Actions
self.action_client = ActionClient(
    NavigateToPose,
    '/navigate_to_pose'
)
```

#### Configuration Integration

```python
def _load_config(self, config_file: Optional[str]) -> dict:
    """Load and validate configuration"""
    default_config = {
        'new_module': {
            'enabled': True,
            'parameter1': 'default_value',
            'parameter2': 42
        }
    }
    
    if config_file and Path(config_file).exists():
        with open(config_file, 'r') as f:
            user_config = yaml.safe_load(f)
            default_config.update(user_config)
    
    return default_config
```

## Adding New Features

### Feature Development Process

1. **Design Phase**:
   - Define feature requirements
   - Design API interface
   - Plan integration points
   - Consider configuration options

2. **Implementation Phase**:
   - Write feature code
   - Add unit tests
   - Update documentation
   - Add configuration options

3. **Testing Phase**:
   - Unit testing
   - Integration testing
   - System testing
   - Performance testing

4. **Documentation Phase**:
   - Update API reference
   - Add user manual section
   - Create examples
   - Update troubleshooting guide

### Example: Adding QR Code Detection

```python
# modules/qr_detection.py
import cv2
import numpy as np
from pyzbar import pyzbar

class QRDetection(Node if 'Node' in globals() else object):
    def __init__(self, config):
        # Initialize as per template
        pass
        
    def detect_qr_codes(self, image):
        """Detect QR codes in image"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        decoded_objects = pyzbar.decode(gray)
        
        qr_codes = []
        for obj in decoded_objects:
            qr_data = obj.data.decode('utf-8')
            qr_type = obj.type
            points = obj.polygon
            
            qr_codes.append({
                'data': qr_data,
                'type': qr_type,
                'points': points
            })
            
        return qr_codes
```

### Integration with Main System

```python
# In turtlebot_automation.py
from modules.qr_detection import QRDetection

# Add to modules
self.modules['qr_detection'] = QRDetection(self.config)

# Initialize in initialize_modules()
for name, module in self.modules.items():
    if hasattr(module, 'initialize'):
        success = module.initialize()
        if not success:
            self.logger.error(f"Failed to initialize {name} module")
            return False
```

## Testing Guidelines

### Unit Testing

#### Test Structure

```python
# tests/test_module_template.py
import unittest
from unittest.mock import Mock, patch
from modules.module_template import ModuleTemplate

class TestModuleTemplate(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            'module_template': {
                'parameter1': 'test_value'
            }
        }
        self.module = ModuleTemplate(self.config)
        
    def test_initialize(self):
        """Test module initialization"""
        result = self.module.initialize()
        self.assertTrue(result)
        
    def test_start_stop(self):
        """Test start and stop functionality"""
        self.module.start()
        self.assertTrue(self.module.is_active)
        
        self.module.stop()
        self.assertFalse(self.module.is_active)
        
    def test_configuration(self):
        """Test configuration handling"""
        self.assertEqual(self.module.config['module_template']['parameter1'], 'test_value')
```

#### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_module_template.py

# Run with coverage
python -m pytest --cov=modules tests/
```

### Integration Testing

#### Test Scenarios

```python
# tests/test_integration.py
import unittest
from turtlebot_automation import TurtleBotAutomation

class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.config = {
            'simulation': {'robot_model': 'waffle'},
            'navigation': {'use_slam': True},
            'detection': {'confidence': 0.5}
        }
        
    def test_full_system_startup(self):
        """Test complete system startup"""
        automation = TurtleBotAutomation(config=self.config, simulation_mode=True)
        
        # Test initialization
        self.assertTrue(automation.initialize_ros())
        self.assertTrue(automation.initialize_modules())
        
        # Test module access
        self.assertIn('navigation', automation.modules)
        self.assertIn('detection', automation.modules)
```

### Performance Testing

#### Benchmarking Framework

```python
# tests/test_performance.py
import time
import unittest
from modules.object_detection import ObjectDetection

class TestPerformance(unittest.TestCase):
    def test_detection_performance(self):
        """Test object detection performance"""
        config = {'detection': {'confidence': 0.5}}
        detector = ObjectDetection(config)
        detector.initialize()
        
        # Test with sample image
        start_time = time.time()
        detections = detector.detect_objects_sync('test_image.jpg')
        end_time = time.time()
        
        processing_time = end_time - start_time
        self.assertLess(processing_time, 1.0)  # Should process in < 1 second
        
        print(f"Detection time: {processing_time:.3f}s")
```

## Debugging Techniques

### Logging Configuration

```python
# Configure logging for development
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)
```

### ROS2 Debugging

#### Node Inspection

```python
# Check node status
ros2 node list

# Check topic information
ros2 topic info /topic_name --verbose

# Monitor topic data
ros2 topic echo /topic_name --once
```

#### Service and Action Debugging

```python
# List available services
ros2 service list

# Call service with debugging
ros2 service call /service_name service_type "{param: value}"

# Monitor action status
ros2 action send /action_name action_type "{goal: {param: value}}"
```

### Performance Profiling

#### CPU Profiling

```python
import cProfile
import pstats

# Profile module execution
cProfile.run('module.run()', 'profile_stats')

# Analyze results
stats = pstats.Stats('profile_stats')
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 functions
```

#### Memory Profiling

```python
import tracemalloc
import gc

# Start memory tracing
tracemalloc.start()

# Run module code
module.run()

# Get memory statistics
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')[:10]

for stat in top_stats:
    print(stat)
```

## Performance Optimization

### Code Optimization

#### Efficient Data Structures

```python
# Use sets for membership testing
valid_objects = {'person', 'car', 'bicycle'}  # O(1) lookup
if object_name in valid_objects:  # Fast lookup
    pass

# Use generators for large datasets
def process_large_list(data):
    for item in data:  # Memory efficient
        yield process_item(item)
```

#### Async Operations

```python
import asyncio
import threading

class AsyncModule:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    def async_process_data(self, data):
        """Process data asynchronously"""
        loop = asyncio.get_event_loop()
        
        # Run blocking operation in thread pool
        future = loop.run_in_executor(
            self.executor, 
            self._blocking_process, 
            data
        )
        
        return await future
        
    def _blocking_process(self, data):
        """Blocking processing operation"""
        # Simulate processing time
        time.sleep(0.1)
        return data * 2
```

### Resource Management

#### Connection Pooling

```python
# Reuse ROS2 connections
class ConnectionPool:
    def __init__(self):
        self.publishers = {}
        self.subscribers = {}
        
    def get_publisher(self, topic_name, msg_type):
        """Get or create publisher"""
        if topic_name not in self.publishers:
            self.publishers[topic_name] = self.create_publisher(
                msg_type, topic_name, 10
            )
        return self.publishers[topic_name]
```

#### Memory Management

```python
# Clear caches periodically
import gc

class MemoryManager:
    def __init__(self, max_cache_size=1000):
        self.cache = {}
        self.max_cache_size = max_cache_size
        
    def get_from_cache(self, key):
        """Get item from cache"""
        return self.cache.get(key)
        
    def add_to_cache(self, key, value):
        """Add item to cache with size limit"""
        if len(self.cache) >= self.max_cache_size:
            # Remove oldest item
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            
        self.cache[key] = value
        
    def clear_cache(self):
        """Clear cache and force garbage collection"""
        self.cache.clear()
        gc.collect()
```

## Contribution Guidelines

### Code Style

#### Python Style Guide

Follow PEP 8 with these additional rules:

```python
# Use descriptive variable names
detection_confidence = 0.5  # Good
conf = 0.5  # Bad

# Use type hints
def process_image(image: np.ndarray) -> List[Dict]:
    """Process image and return detections"""
    pass

# Docstrings for all public functions
def navigate_to_pose(x: float, y: float, yaw: float) -> bool:
    """
    Navigate robot to specified pose.
    
    Args:
        x: Target X coordinate
        y: Target Y coordinate
        yaw: Target yaw angle in radians
        
    Returns:
        True if navigation started successfully
    """
    pass
```

#### Import Organization

```python
# Standard library imports first
import os
import sys
import time
import logging
from typing import Dict, List, Optional

# Third-party imports
import numpy as np
import cv2

# ROS2 imports (with fallbacks)
try:
    import rclpy
    from rclpy.node import Node
    from std_msgs.msg import String
except ImportError:
    Node = object
    String = object

# Local imports
from modules.module_template import ModuleTemplate
```

### Commit Guidelines

#### Commit Message Format

```
type(scope): brief description

Detailed explanation of changes and reasoning.

Fixes #123: Correct bug in navigation module
- Add error handling for invalid poses
- Improve performance of path planning

Closes #456
```

#### Branch Naming

```
feature/add-qr-detection    # New feature
bugfix/navigation-timeout   # Bug fix
hotfix/critical-memory-leak  # Hotfix
refactor/module-structure     # Refactoring
docs/update-api-reference     # Documentation
```

### Pull Request Process

1. **Fork Repository**
2. **Create Feature Branch**
3. **Make Changes**
4. **Add Tests**
5. **Update Documentation**
6. **Submit Pull Request**

#### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No breaking changes
```

This developer guide provides comprehensive information for extending and contributing to the TurtleBot3 automation system. Follow these guidelines to ensure high-quality, maintainable code.
# Examples and Use Cases

This document provides practical examples and use cases for the TurtleBot3 automation system.

## Table of Contents

- [Basic Usage Examples](#basic-usage-examples)
- [Navigation Examples](#navigation-examples)
- [Object Detection Examples](#object-detection-examples)
- [Voice Control Examples](#voice-control-examples)
- [Integration Examples](#integration-examples)
- [Advanced Scenarios](#advanced-scenarios)
- [Custom Extensions](#custom-extensions)

## Basic Usage Examples

### Quick Start with Simulation

```python
#!/usr/bin/env python3
"""
Basic example: Start full automation system in simulation
"""

from turtlebot_automation import TurtleBotAutomation

def main():
    # Create automation instance with default settings
    automation = TurtleBotAutomation(simulation_mode=True)
    
    # Run full system
    try:
        automation.run_full_automation()
    except KeyboardInterrupt:
        print("Shutting down...")
        automation.shutdown()

if __name__ == "__main__":
    main()
```

### Individual Module Testing

```python
#!/usr/bin/env python3
"""
Test individual modules independently
"""

from modules.setup_automation import SetupAutomation
from modules.maintenance_automation import MaintenanceAutomation
from modules.navigation_automation import NavigationAutomation
from modules.object_detection import ObjectDetection
from modules.voice_control import VoiceControl

def test_setup():
    """Test setup automation"""
    config = {"simulation": {"robot_model": "waffle"}}
    setup = SetupAutomation(config, simulation_mode=True)
    
    if setup.initialize():
        print("Setup module initialized successfully")
        if setup.needs_setup():
            print("Running setup...")
            setup.run_setup()
    else:
        print("Setup initialization failed")

def test_maintenance():
    """Test maintenance monitoring"""
    config = {"maintenance": {"health_check_interval": 10.0}}
    maintenance = MaintenanceAutomation(config)
    
    if maintenance.initialize():
        print("Maintenance module initialized")
        maintenance.start_monitoring()
        
        # Monitor for 30 seconds
        import time
        time.sleep(30)
        
        # Get health report
        report = maintenance.get_health_report()
        print(f"System healthy: {report['healthy']}")
        print(f"Battery: {report['battery']['percentage']:.1f}%")
        
        maintenance.stop_monitoring()

def test_navigation():
    """Test navigation system"""
    config = {"navigation": {"use_slam": True}}
    nav = NavigationAutomation(config, simulation_mode=True)
    
    if nav.initialize():
        print("Navigation module initialized")
        nav.start_navigation()
        
        # Navigate to specific location
        success = nav.navigate_to_pose(2.0, 3.0, 1.57)
        print(f"Navigation started: {success}")
        
        # Wait for navigation to complete
        import time
        time.sleep(10)
        
        nav.stop_navigation()

def test_detection():
    """Test object detection"""
    config = {"detection": {"confidence": 0.5}}
    detector = ObjectDetection(config)
    
    if detector.initialize():
        print("Object detection initialized")
        detector.start_detection()
        
        # Test with sample image
        detections = detector.detect_objects_sync("test_image.jpg")
        print(f"Found {len(detections)} objects")
        
        for detection in detections:
            print(f"  {detection['class_name']}: {detection['confidence']:.2f}")
        
        detector.stop_detection()

def test_voice():
    """Test voice control"""
    config = {"voice": {"wake_word": "turtlebot"}}
    voice = VoiceControl(config)
    
    if voice.initialize():
        print("Voice control initialized")
        voice.start_voice_control()
        
        # Add custom location
        voice.add_location("test_room", 1.0, 1.0, 0.0)
        
        # Get all locations
        locations = voice.get_locations()
        print(f"Available locations: {list(locations.keys())}")
        
        # Test for 10 seconds
        import time
        time.sleep(10)
        
        voice.stop_voice_control()

if __name__ == "__main__":
    print("Testing individual modules...")
    
    print("\n1. Testing Setup...")
    test_setup()
    
    print("\n2. Testing Maintenance...")
    test_maintenance()
    
    print("\n3. Testing Navigation...")
    test_navigation()
    
    print("\n4. Testing Object Detection...")
    test_detection()
    
    print("\n5. Testing Voice Control...")
    test_voice()
```

## Navigation Examples

### Autonomous Room Mapping

```python
#!/usr/bin/env python3
"""
Example: Autonomous room mapping with SLAM
"""

from modules.navigation_automation import NavigationAutomation
import time
import math

class RoomMapper:
    def __init__(self, config):
        self.nav = NavigationAutomation(config, simulation_mode=True)
        self.waypoints = []
        self.current_index = 0
        
    def generate_room_waypoints(self, room_size=5.0):
        """Generate waypoints for systematic room exploration"""
        waypoints = []
        
        # Perimeter waypoints
        perimeter = [
            (0.0, 0.0, 0.0),
            (room_size, 0.0, math.pi/2),
            (room_size, room_size, math.pi),
            (0.0, room_size, -math.pi/2),
            (0.0, 0.0, 0.0)
        ]
        
        # Grid waypoints for coverage
        grid_spacing = 1.0
        for x in range(0, int(room_size), int(grid_spacing)):
            for y in range(0, int(room_size), int(grid_spacing)):
                waypoints.append((x, y, 0.0))
        
        return perimeter + waypoints
    
    def start_mapping(self):
        """Start autonomous mapping"""
        if not self.nav.initialize():
            print("Failed to initialize navigation")
            return
            
        self.nav.start_navigation()
        
        # Generate waypoints
        self.waypoints = self.generate_room_waypoints()
        print(f"Generated {len(self.waypoints)} waypoints for mapping")
        
        # Start waypoint following
        self.follow_waypoints()
    
    def follow_waypoints(self):
        """Follow waypoints for complete coverage"""
        for i, (x, y, yaw) in enumerate(self.waypoints):
            print(f"Navigating to waypoint {i+1}/{len(self.waypoints)}: ({x}, {y}, {yaw})")
            
            success = self.nav.navigate_to_pose(x, y, yaw)
            if not success:
                print(f"Failed to navigate to waypoint {i+1}")
                continue
                
            # Wait for navigation to complete
            self.wait_for_navigation_complete()
            
            # Brief pause at each waypoint
            time.sleep(2)
    
    def wait_for_navigation_complete(self):
        """Wait for current navigation to complete"""
        while self.nav.is_navigation_active():
            time.sleep(0.5)
    
    def save_map(self, map_name="room_map"):
        """Save the generated map"""
        print(f"Saving map as {map_name}")
        # This would integrate with Nav2 map saving
        # ros2 run nav2_map_server map_saver_cli -f room_map

def main():
    config = {
        "navigation": {
            "use_slam": True,
            "localization": False
        }
    }
    
    mapper = RoomMapper(config)
    mapper.start_mapping()
    
    # Keep running for mapping
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Mapping complete!")
        mapper.save_map()
        mapper.nav.shutdown()

if __name__ == "__main__":
    main()
```

### Multi-Room Navigation

```python
#!/usr/bin/env python3
"""
Example: Navigate between multiple rooms
"""

from modules.navigation_automation import NavigationAutomation
import time

class MultiRoomNavigator:
    def __init__(self, config):
        self.nav = NavigationAutomation(config, simulation_mode=True)
        
        # Define room locations
        self.rooms = {
            "kitchen": (3.0, 2.0, 0.0),
            "living_room": (1.0, 1.0, 1.57),
            "bedroom": (2.0, 3.0, -1.57),
            "bathroom": (4.0, 1.0, 0.0),
            "entrance": (0.0, 0.0, 0.0)
        }
    
    def start_navigation(self):
        """Start multi-room navigation system"""
        if not self.nav.initialize():
            return
            
        self.nav.start_navigation()
        
        # Interactive room selection
        while True:
            self.print_available_rooms()
            room = input("Enter room name (or 'quit'): ").strip().lower()
            
            if room == 'quit':
                break
            elif room in self.rooms:
                self.navigate_to_room(room)
            else:
                print("Unknown room. Available rooms:", list(self.rooms.keys()))
    
    def print_available_rooms(self):
        """Print available rooms"""
        print("\nAvailable rooms:")
        for room, (x, y, yaw) in self.rooms.items():
            print(f"  {room}: ({x:.1f}, {y:.1f}, {math.degrees(yaw):.0f}°)")
    
    def navigate_to_room(self, room_name):
        """Navigate to specific room"""
        x, y, yaw = self.rooms[room_name]
        print(f"Navigating to {room_name}...")
        
        success = self.nav.navigate_to_pose(x, y, yaw)
        if success:
            print(f"Navigation to {room_name} started successfully")
            self.wait_for_arrival(room_name)
        else:
            print(f"Failed to start navigation to {room_name}")
    
    def wait_for_arrival(self, room_name):
        """Wait until robot arrives at destination"""
        print(f"Traveling to {room_name}...")
        
        start_time = time.time()
        timeout = 30.0  # 30 second timeout
        
        while self.nav.is_navigation_active():
            if time.time() - start_time > timeout:
                print(f"Timeout reached for {room_name}")
                break
            time.sleep(0.5)
        
        print(f"Arrived at {room_name}")

def main():
    config = {
        "navigation": {
            "use_slam": False,
            "localization": True
        }
    }
    
    navigator = MultiRoomNavigator(config)
    navigator.start_navigation()

if __name__ == "__main__":
    main()
```

## Object Detection Examples

### Real-time Object Detection with Alerts

```python
#!/usr/bin/env python3
"""
Example: Real-time object detection with custom alerts
"""

from modules.object_detection import ObjectDetection
import time

class SecurityMonitor:
    def __init__(self, config):
        self.detector = ObjectDetection(config)
        self.alert_objects = ["person", "car", "truck"]
        self.last_alerts = {}
        
    def start_monitoring(self):
        """Start security monitoring"""
        if not self.detector.initialize():
            print("Failed to initialize object detector")
            return
            
        self.detector.start_detection()
        print("Security monitoring started")
        
        # Monitor for detections
        self.monitor_detections()
    
    def monitor_detections(self):
        """Monitor for security-relevant objects"""
        try:
            while True:
                # Get detection statistics
                stats = self.detector.get_detection_stats()
                
                # Check for recent detections
                if stats['total_detections'] > 0:
                    print(f"Active monitoring - FPS: {stats['current_fps']:.1f}")
                
                time.sleep(5)  # Check every 5 seconds
                
        except KeyboardInterrupt:
            print("Stopping security monitoring...")
    
    def process_detection(self, detection):
        """Process individual detection for security alerts"""
        object_name = detection['class_name']
        confidence = detection['confidence']
        
        # Check if this is an alert-worthy object
        if object_name in self.alert_objects and confidence > 0.7:
            current_time = time.time()
            
            # Check if we recently alerted for this object
            if (object_name not in self.last_alerts or 
                current_time - self.last_alerts[object_name] > 30):
                
                self.send_alert(object_name, detection)
                self.last_alerts[object_name] = current_time
    
    def send_alert(self, object_name, detection):
        """Send security alert"""
        bbox = detection['bbox']
        x1, y1, x2, y2 = bbox
        
        print(f"🚨 SECURITY ALERT: {object_name.upper()} DETECTED!")
        print(f"   Location: ({x1:.0f}, {y1:.0f}) to ({x2:.0f}, {y2:.0f})")
        print(f"   Confidence: {detection['confidence']:.2f}")
        print(f"   Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Here you could add:
        # - Email notifications
        # - SMS alerts
        # - Security system integration
        # - Logging to file

def main():
    config = {
        "detection": {
            "confidence": 0.5,
            "camera_topic": "/camera/image_raw"
        }
    }
    
    monitor = SecurityMonitor(config)
    monitor.start_monitoring()

if __name__ == "__main__":
    main()
```

### Object Counting and Statistics

```python
#!/usr/bin/env python3
"""
Example: Object counting and statistics collection
"""

from modules.object_detection import ObjectDetection
import time
import json
from collections import defaultdict

class ObjectCounter:
    def __init__(self, config):
        self.detector = ObjectDetection(config)
        self.object_counts = defaultdict(int)
        self.session_start = time.time()
        self.detection_history = []
        
    def start_counting(self):
        """Start object counting session"""
        if not self.detector.initialize():
            return
            
        self.detector.start_detection()
        print("Object counting session started")
        
        # Run counting for specified duration
        self.count_objects(duration=60)  # Count for 60 seconds
    
    def count_objects(self, duration=60):
        """Count objects for specified duration"""
        start_time = time.time()
        
        try:
            while time.time() - start_time < duration:
                # Get current detection stats
                stats = self.detector.get_detection_stats()
                
                # Simulate processing current detections
                # In real implementation, this would process actual detection data
                self.process_current_detections()
                
                time.sleep(1)  # Check every second
                
        except KeyboardInterrupt:
            print("Counting interrupted by user")
        
        self.generate_report()
    
    def process_current_detections(self):
        """Process current frame detections"""
        # This would integrate with actual detection callback
        # For demonstration, we'll simulate some detections
        pass
    
    def add_detection(self, detection):
        """Add a detection to the count"""
        object_name = detection['class_name']
        confidence = detection['confidence']
        
        # Only count high-confidence detections
        if confidence > 0.6:
            self.object_counts[object_name] += 1
            
            # Store detection with timestamp
            self.detection_history.append({
                'object': object_name,
                'confidence': confidence,
                'timestamp': time.time(),
                'bbox': detection['bbox']
            })
    
    def generate_report(self):
        """Generate comprehensive counting report"""
        session_duration = time.time() - self.session_start
        
        print(f"\n{'='*50}")
        print(f"OBJECT COUNTING REPORT")
        print(f"{'='*50}")
        print(f"Session Duration: {session_duration:.1f} seconds")
        print(f"Total Detections: {len(self.detection_history)}")
        print(f"Unique Objects: {len(self.object_counts)}")
        
        print(f"\nObject Counts:")
        for object_name, count in sorted(self.object_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {object_name}: {count}")
        
        # Calculate detection rate
        detection_rate = len(self.detection_history) / session_duration
        print(f"\nDetection Rate: {detection_rate:.2f} detections/second")
        
        # Save report to file
        self.save_report()
    
    def save_report(self):
        """Save report to JSON file"""
        report_data = {
            'session_duration': time.time() - self.session_start,
            'total_detections': len(self.detection_history),
            'object_counts': dict(self.object_counts),
            'detection_history': self.detection_history,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        filename = f"object_counting_report_{int(time.time())}.json"
        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\nReport saved to: {filename}")

def main():
    config = {
        "detection": {
            "confidence": 0.6,
            "max_detections": 50
        }
    }
    
    counter = ObjectCounter(config)
    counter.start_counting()

if __name__ == "__main__":
    main()
```

## Voice Control Examples

### Voice-Controlled Home Assistant

```python
#!/usr/bin/env python3
"""
Example: Voice-controlled home assistant robot
"""

from modules.voice_control import VoiceControl
from modules.navigation_automation import NavigationAutomation
import time

class HomeAssistant:
    def __init__(self, config):
        self.voice = VoiceControl(config)
        self.nav = NavigationAutomation(config, simulation_mode=True)
        
        # Home locations
        self.locations = {
            "kitchen": (3.0, 2.0, 0.0),
            "living room": (1.0, 1.0, 1.57),
            "bedroom": (2.0, 3.0, -1.57),
            "office": (4.0, 1.0, 1.57),
            "entrance": (0.0, 0.0, 0.0)
        }
        
        # Add locations to voice control
        for name, coords in self.locations.items():
            self.voice.add_location(name, *coords)
    
    def start_assistant(self):
        """Start home assistant"""
        if not self.voice.initialize() or not self.nav.initialize():
            print("Failed to initialize systems")
            return
            
        self.voice.start_voice_control()
        self.nav.start_navigation()
        
        print("Home Assistant ready! Say 'Hey robot' followed by a command.")
        print("Commands: 'go to [room]', 'come here', 'what do you see', 'stop'")
        
        # Keep running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Shutting down Home Assistant...")
            self.shutdown()
    
    def shutdown(self):
        """Graceful shutdown"""
        self.voice.stop_voice_control()
        self.nav.stop_navigation()

def main():
    config = {
        "voice": {
            "wake_word": "hey robot",
            "recognition_engine": "google"
        },
        "navigation": {
            "use_slam": False,
            "localization": True
        }
    }
    
    assistant = HomeAssistant(config)
    assistant.start_assistant()

if __name__ == "__main__":
    main()
```

### Voice-Controlled Inspection Robot

```python
#!/usr/bin/env python3
"""
Example: Voice-controlled inspection robot
"""

from modules.voice_control import VoiceControl
from modules.object_detection import ObjectDetection
from modules.navigation_automation import NavigationAutomation
import time
import json

class InspectionRobot:
    def __init__(self, config):
        self.voice = VoiceControl(config)
        self.detector = ObjectDetection(config)
        self.nav = NavigationAutomation(config, simulation_mode=True)
        
        # Inspection waypoints
        self.inspection_points = [
            (1.0, 1.0, 0.0, "Entry Point"),
            (2.0, 1.0, 0.0, "Corridor"),
            (3.0, 1.0, 0.0, "Room 1"),
            (3.0, 2.0, 1.57, "Room 1 Corner"),
            (3.0, 3.0, 1.57, "Room 2"),
            (2.0, 3.0, 0.0, "Room 2 Corner"),
            (1.0, 3.0, -1.57, "Room 3"),
            (1.0, 2.0, -1.57, "Center")
        ]
        
        self.current_point = 0
        self.inspection_log = []
    
    def start_inspection(self):
        """Start automated inspection"""
        if not all([self.voice.initialize(), self.detector.initialize(), self.nav.initialize()]):
            print("Failed to initialize inspection systems")
            return
            
        self.voice.start_voice_control()
        self.detector.start_detection()
        self.nav.start_navigation()
        
        print("Inspection robot ready!")
        print("Commands: 'start inspection', 'next point', 'report', 'stop'")
        
        # Keep running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.shutdown()
    
    def execute_inspection_sequence(self):
        """Execute complete inspection sequence"""
        print("Starting inspection sequence...")
        
        for i, (x, y, yaw, name) in enumerate(self.inspection_points):
            print(f"Moving to inspection point {i+1}/{len(self.inspection_points)}: {name}")
            
            # Navigate to point
            success = self.nav.navigate_to_pose(x, y, yaw)
            if not success:
                print(f"Failed to navigate to {name}")
                continue
            
            # Wait for arrival
            self.wait_for_navigation_complete()
            
            # Perform inspection at this point
            self.inspect_point(name, x, y, yaw)
            
            # Brief pause for inspection
            time.sleep(3)
        
        print("Inspection sequence complete!")
        self.generate_inspection_report()
    
    def inspect_point(self, point_name, x, y, yaw):
        """Perform inspection at current point"""
        print(f"Inspecting {point_name}...")
        
        # Capture detection data
        start_time = time.time()
        detections = []
        
        # Collect detections for 2 seconds
        while time.time() - start_time < 2:
            # In real implementation, this would collect actual detections
            # For demonstration, simulate some detections
            pass
            time.sleep(0.1)
        
        # Log inspection results
        inspection_data = {
            'point_name': point_name,
            'coordinates': (x, y, yaw),
            'timestamp': time.time(),
            'detections': detections,
            'status': 'completed'
        }
        
        self.inspection_log.append(inspection_data)
        print(f"Inspection at {point_name} completed")
    
    def wait_for_navigation_complete(self):
        """Wait for navigation to complete"""
        while self.nav.is_navigation_active():
            time.sleep(0.5)
    
    def generate_inspection_report(self):
        """Generate inspection report"""
        report = {
            'inspection_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_points': len(self.inspection_points),
            'completed_points': len(self.inspection_log),
            'inspection_log': self.inspection_log
        }
        
        filename = f"inspection_report_{int(time.time())}.json"
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Inspection report saved to: {filename}")
    
    def shutdown(self):
        """Shutdown inspection robot"""
        self.voice.stop_voice_control()
        self.detector.stop_detection()
        self.nav.stop_navigation()

def main():
    config = {
        "voice": {"wake_word": "robot"},
        "detection": {"confidence": 0.7},
        "navigation": {"localization": True}
    }
    
    inspector = InspectionRobot(config)
    inspector.start_inspection()

if __name__ == "__main__":
    main()
```

## Integration Examples

### Web Interface Integration

```python
#!/usr/bin/env python3
"""
Example: Web interface for TurtleBot3 control
"""

from flask import Flask, jsonify, request
from modules.navigation_automation import NavigationAutomation
from modules.object_detection import ObjectDetection
from modules.maintenance_automation import MaintenanceAutomation
import threading
import time

class WebInterface:
    def __init__(self, config):
        self.app = Flask(__name__)
        self.nav = NavigationAutomation(config, simulation_mode=True)
        self.detector = ObjectDetection(config)
        self.maintenance = MaintenanceAutomation(config)
        
        # Initialize systems
        self.nav.initialize()
        self.detector.initialize()
        self.maintenance.initialize()
        
        # Start background processes
        self.nav.start_navigation()
        self.detector.start_detection()
        self.maintenance.start_monitoring()
        
        # Setup routes
        self.setup_routes()
    
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            return jsonify({
                'status': 'TurtleBot3 Web Interface',
                'endpoints': [
                    '/status',
                    '/navigate',
                    '/detections',
                    '/health',
                    '/locations'
                ]
            })
        
        @self.app.route('/status')
        def get_status():
            return jsonify({
                'navigation_active': self.nav.is_navigation_active(),
                'detection_active': self.detector.get_detection_stats()['is_active'],
                'system_healthy': self.maintenance.is_healthy()
            })
        
        @self.app.route('/navigate', methods=['POST'])
        def navigate():
            data = request.json
            x = data.get('x', 0.0)
            y = data.get('y', 0.0)
            yaw = data.get('yaw', 0.0)
            
            success = self.nav.navigate_to_pose(x, y, yaw)
            return jsonify({
                'success': success,
                'target': {'x': x, 'y': y, 'yaw': yaw}
            })
        
        @self.app.route('/detections')
        def get_detections():
            stats = self.detector.get_detection_stats()
            return jsonify(stats)
        
        @self.app.route('/health')
        def get_health():
            report = self.maintenance.get_health_report()
            return jsonify(report)
        
        @self.app.route('/locations')
        def get_locations():
            # Return predefined navigation locations
            locations = {
                'kitchen': {'x': 3.0, 'y': 2.0, 'yaw': 0.0},
                'living_room': {'x': 1.0, 'y': 1.0, 'yaw': 1.57},
                'bedroom': {'x': 2.0, 'y': 3.0, 'yaw': -1.57},
                'entrance': {'x': 0.0, 'y': 0.0, 'yaw': 0.0}
            }
            return jsonify(locations)
    
    def run(self, host='0.0.0.0', port=5000):
        """Run web interface"""
        self.app.run(host=host, port=port, debug=False)

def main():
    config = {
        "navigation": {"localization": True},
        "detection": {"confidence": 0.5},
        "maintenance": {"health_check_interval": 30.0}
    }
    
    web_interface = WebInterface(config)
    print("Starting web interface at http://localhost:5000")
    web_interface.run()

if __name__ == "__main__":
    main()
```

### Mobile App Integration

```python
#!/usr/bin/env python3
"""
Example: Mobile app backend for TurtleBot3 control
"""

from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from modules.navigation_automation import NavigationAutomation
from modules.voice_control import VoiceControl
import json

class MobileAppBackend:
    def __init__(self, config):
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        self.nav = NavigationAutomation(config, simulation_mode=True)
        self.voice = VoiceControl(config)
        
        # Initialize systems
        self.nav.initialize()
        self.voice.initialize()
        self.nav.start_navigation()
        
        # Setup routes and socket events
        self.setup_routes()
        self.setup_socket_events()
    
    def setup_routes(self):
        """Setup REST API routes"""
        
        @self.app.route('/api/status')
        def api_status():
            return jsonify({
                'connected': True,
                'navigation_active': self.nav.is_navigation_active(),
                'voice_active': self.voice.is_listening_active()
            })
        
        @self.app.route('/api/locations')
        def api_locations():
            return jsonify(self.voice.get_locations())
    
    def setup_socket_events(self):
        """Setup WebSocket events for real-time communication"""
        
        @self.socketio.on('connect')
        def handle_connect():
            print('Mobile app connected')
            emit('status', {'connected': True})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            print('Mobile app disconnected')
        
        @self.socketio.on('navigate')
        def handle_navigate(data):
            x = data.get('x', 0.0)
            y = data.get('y', 0.0)
            yaw = data.get('yaw', 0.0)
            
            success = self.nav.navigate_to_pose(x, y, yaw)
            emit('navigation_result', {
                'success': success,
                'target': {'x': x, 'y': y, 'yaw': yaw}
            })
        
        @self.socketio.on('voice_command')
        def handle_voice_command(command):
            # Process voice command
            self.voice._process_voice_command(command)
            emit('voice_processed', {'command': command})
        
        @self.socketio.on('stop')
        def handle_stop():
            self.nav.stop_robot()
            emit('stopped', {'status': 'stopped'})
    
    def run(self, host='0.0.0.0', port=5001):
        """Run mobile app backend"""
        self.socketio.run(self.app, host=host, port=port, debug=False)

def main():
    config = {
        "navigation": {"localization": True},
        "voice": {"wake_word": "robot"}
    }
    
    backend = MobileAppBackend(config)
    print("Mobile app backend running on ws://localhost:5001")
    backend.run()

if __name__ == "__main__":
    main()
```

## Advanced Scenarios

### Autonomous Delivery Robot

```python
#!/usr/bin/env python3
"""
Example: Autonomous delivery robot with multiple stops
"""

from modules.navigation_automation import NavigationAutomation
from modules.object_detection import ObjectDetection
from modules.voice_control import VoiceControl
import time
import threading

class DeliveryRobot:
    def __init__(self, config):
        self.nav = NavigationAutomation(config, simulation_mode=True)
        self.detector = ObjectDetection(config)
        self.voice = VoiceControl(config)
        
        # Delivery locations
        self.delivery_locations = [
            {"name": "Pickup Point", "coords": (0.0, 0.0, 0.0), "type": "pickup"},
            {"name": "Delivery 1", "coords": (2.0, 1.0, 0.0), "type": "delivery"},
            {"name": "Delivery 2", "coords": (3.0, 2.0, 1.57), "type": "delivery"},
            {"name": "Delivery 3", "coords": (1.0, 3.0, -1.57), "type": "delivery"},
            {"name": "Return Point", "coords": (0.0, 0.0, 0.0), "type": "return"}
        ]
        
        self.current_location = 0
        self.delivery_log = []
        
    def start_delivery_service(self):
        """Start delivery service"""
        if not all([self.nav.initialize(), self.detector.initialize(), self.voice.initialize()]):
            print("Failed to initialize delivery systems")
            return
            
        self.nav.start_navigation()
        self.detector.start_detection()
        self.voice.start_voice_control()
        
        print("Delivery robot ready!")
        print("Commands: 'start delivery', 'status', 'emergency stop'")
        
        # Start delivery loop in background
        delivery_thread = threading.Thread(target=self.delivery_loop, daemon=True)
        delivery_thread.start()
        
        # Keep main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.shutdown()
    
    def delivery_loop(self):
        """Main delivery loop"""
        while True:
            # Wait for delivery command
            time.sleep(1)
    
    def execute_delivery_route(self):
        """Execute complete delivery route"""
        print("Starting delivery route...")
        
        for i, location in enumerate(self.delivery_locations):
            self.current_location = i
            coords = location["coords"]
            name = location["name"]
            location_type = location["type"]
            
            print(f"Traveling to {name} ({location_type})...")
            
            # Navigate to location
            success = self.nav.navigate_to_pose(*coords)
            if not success:
                print(f"Failed to navigate to {name}")
                continue
            
            # Wait for arrival
            self.wait_for_arrival()
            
            # Handle location type
            if location_type == "pickup":
                self.handle_pickup(name)
            elif location_type == "delivery":
                self.handle_delivery(name)
            elif location_type == "return":
                self.handle_return(name)
            
            # Brief pause at each location
            time.sleep(2)
        
        print("Delivery route completed!")
        self.generate_delivery_report()
    
    def handle_pickup(self, location_name):
        """Handle pickup at location"""
        print(f"Handling pickup at {location_name}")
        
        # Look for delivery object
        print("Scanning for delivery object...")
        time.sleep(2)
        
        # Log pickup
        self.delivery_log.append({
            'action': 'pickup',
            'location': location_name,
            'timestamp': time.time(),
            'status': 'completed'
        })
        
        # Voice confirmation
        self.voice.speak(f"Picked up item at {location_name}")
    
    def handle_delivery(self, location_name):
        """Handle delivery at location"""
        print(f"Handling delivery at {location_name}")
        
        # Look for clear delivery space
        print("Scanning delivery area...")
        time.sleep(2)
        
        # Log delivery
        self.delivery_log.append({
            'action': 'delivery',
            'location': location_name,
            'timestamp': time.time(),
            'status': 'completed'
        })
        
        # Voice confirmation
        self.voice.speak(f"Delivered item at {location_name}")
    
    def handle_return(self, location_name):
        """Handle return to base"""
        print(f"Returning to {location_name}")
        
        # Log return
        self.delivery_log.append({
            'action': 'return',
            'location': location_name,
            'timestamp': time.time(),
            'status': 'completed'
        })
        
        # Voice confirmation
        self.voice.speak(f"Returned to {location_name}")
    
    def wait_for_arrival(self):
        """Wait for navigation to complete"""
        while self.nav.is_navigation_active():
            time.sleep(0.5)
    
    def generate_delivery_report(self):
        """Generate delivery report"""
        report = {
            'delivery_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_locations': len(self.delivery_locations),
            'delivery_log': self.delivery_log
        }
        
        filename = f"delivery_report_{int(time.time())}.json"
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Delivery report saved to: {filename}")
    
    def shutdown(self):
        """Shutdown delivery robot"""
        self.voice.stop_voice_control()
        self.detector.stop_detection()
        self.nav.stop_navigation()

def main():
    config = {
        "navigation": {"localization": True},
        "detection": {"confidence": 0.6},
        "voice": {"wake_word": "delivery bot"}
    }
    
    delivery_robot = DeliveryRobot(config)
    delivery_robot.start_delivery_service()

if __name__ == "__main__":
    main()
```

## Custom Extensions

### Custom Behavior Tree

```python
#!/usr/bin/env python3
"""
Example: Custom behavior tree for robot decision making
"""

from modules.navigation_automation import NavigationAutomation
from modules.object_detection import ObjectDetection
import time
import threading

class BehaviorNode:
    def __init__(self, name):
        self.name = name
        self.status = "idle"
    
    def execute(self):
        raise NotImplementedError

class NavigateToNode(BehaviorNode):
    def __init__(self, nav, x, y, yaw):
        super().__init__(f"NavigateTo({x},{y},{yaw})")
        self.nav = nav
        self.x = x
        self.y = y
        self.yaw = yaw
    
    def execute(self):
        self.status = "running"
        success = self.nav.navigate_to_pose(self.x, self.y, self.yaw)
        self.status = "completed" if success else "failed"
        return success

class DetectObjectsNode(BehaviorNode):
    def __init__(self, detector, target_objects):
        super().__init__(f"DetectObjects({target_objects})")
        self.detector = detector
        self.target_objects = target_objects
    
    def execute(self):
        self.status = "running"
        # Check for target objects
        stats = self.detector.get_detection_stats()
        # In real implementation, check actual detections
        self.status = "completed"
        return True

class BehaviorTree:
    def __init__(self, nav, detector):
        self.nav = nav
        self.detector = detector
        self.root = None
    
    def create_patrol_tree(self):
        """Create a patrol behavior tree"""
        # Sequence: Navigate -> Detect -> Navigate -> Detect -> ...
        patrol_points = [
            (1.0, 1.0, 0.0),
            (2.0, 1.0, 0.0),
            (2.0, 2.0, 1.57),
            (1.0, 2.0, -1.57)
        ]
        
        nodes = []
        for i, (x, y, yaw) in enumerate(patrol_points):
            navigate = NavigateToNode(self.nav, x, y, yaw)
            detect = DetectObjectsNode(self.detector, ["person", "package"])
            nodes.extend([navigate, detect])
        
        self.root = nodes[0]  # Start with first navigate node
        return nodes
    
    def execute_tree(self):
        """Execute behavior tree"""
        nodes = self.create_patrol_tree()
        
        for node in nodes:
            print(f"Executing: {node.name}")
            success = node.execute()
            print(f"Result: {node.status}")
            
            if not success:
                print(f"Behavior failed at {node.name}")
                break
            
            time.sleep(1)  # Brief pause between actions

def main():
    config = {
        "navigation": {"localization": True},
        "detection": {"confidence": 0.5}
    }
    
    nav = NavigationAutomation(config, simulation_mode=True)
    detector = ObjectDetection(config)
    
    nav.initialize()
    detector.initialize()
    nav.start_navigation()
    detector.start_detection()
    
    # Create and execute behavior tree
    tree = BehaviorTree(nav, detector)
    tree.execute_tree()

if __name__ == "__main__":
    main()
```

These examples demonstrate various ways to use and extend the TurtleBot3 automation system. Each example can be adapted for specific use cases and requirements.
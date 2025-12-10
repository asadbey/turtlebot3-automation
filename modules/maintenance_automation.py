#!/usr/bin/env python3
"""
Maintenance Automation Module for TurtleBot3
Handles health monitoring, diagnostics, and system maintenance
Supports both simulation and hardware deployment
"""

import rclpy
import time
import threading
import logging
from typing import Dict, List, Optional
from pathlib import Path

# ROS2 imports
try:
    from rclpy.node import Node
    from sensor_msgs.msg import BatteryState, Imu, LaserScan
    from nav_msgs.msg import Odometry
    from diagnostic_msgs.msg import DiagnosticArray, DiagnosticStatus
    from std_msgs.msg import Header
except ImportError:
    # Fallback for systems without ROS2 installed
    Node = object
    BatteryState = object
    Imu = object
    LaserScan = object
    Odometry = object
    DiagnosticArray = object
    DiagnosticStatus = object
    Header = object


class MaintenanceAutomation(Node if 'Node' in globals() else object):
    """Automates health monitoring and maintenance for TurtleBot3"""
    
    def __init__(self, config: Dict):
        """
        Initialize maintenance automation
        
        Args:
            config: Configuration dictionary
        """
        # Initialize ROS node if available
        if 'Node' in globals():
            super().__init__('maintenance_automation')
            
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.health_check_interval = config.get('maintenance', {}).get('health_check_interval', 30.0)
        self.battery_threshold = config.get('maintenance', {}).get('battery_threshold', 20.0)
        
        # State tracking
        self.is_monitoring = False
        self.monitoring_thread = None
        self.system_health = {
            'battery': {'status': 'unknown', 'voltage': 0.0, 'percentage': 100.0},
            'sensors': {'lidar': 'unknown', 'imu': 'unknown', 'camera': 'unknown'},
            'motors': {'status': 'unknown', 'left_wheel': 0.0, 'right_wheel': 0.0},
            'navigation': {'status': 'unknown', 'localization': 'unknown'},
            'system': {'cpu_usage': 0.0, 'memory_usage': 0.0, 'disk_usage': 0.0}
        }
        
        # ROS2 subscribers (will be initialized in initialize())
        self.battery_sub = None
        self.imu_sub = None
        self.lidar_sub = None
        self.odom_sub = None
        self.diagnostic_pub = None
        
    def initialize(self) -> bool:
        """Initialize maintenance module"""
        try:
            self.logger.info("Initializing maintenance automation module")

            if 'Node' in globals():
                self._setup_ros_connections()
                self.logger.info("ROS2 connections established for maintenance monitoring")
            else:
                self.logger.info("ROS2 not available, running in simulation mode with mock data")
                self._start_simulation_mode()

            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize maintenance module: {e}")
            return False
            
    def _setup_ros_connections(self) -> None:
        """Setup ROS2 subscribers and publishers"""
        try:
            # Battery status subscriber
            self.battery_sub = self.create_subscription(
                BatteryState,
                '/battery_status',
                self._battery_callback,
                10
            )

            # IMU subscriber
            self.imu_sub = self.create_subscription(
                Imu,
                '/imu',
                self._imu_callback,
                10
            )

            # LIDAR subscriber
            self.lidar_sub = self.create_subscription(
                LaserScan,
                '/scan',
                self._lidar_callback,
                10
            )

            # Odometry subscriber
            self.odom_sub = self.create_subscription(
                Odometry,
                '/odom',
                self._odom_callback,
                10
            )

            # Diagnostics publisher
            self.diagnostic_pub = self.create_publisher(
                DiagnosticArray,
                '/diagnostics',
                10
            )

            self.logger.info("ROS2 connections established")

        except Exception as e:
            self.logger.error(f"Failed to setup ROS connections: {e}")

    def _start_simulation_mode(self) -> None:
        """Start simulation mode with mock data generation"""
        self.logger.info("Starting maintenance simulation mode")
        # Initialize mock data
        self._last_battery_time = time.time()
        self._last_lidar_time = time.time()
        self._last_imu_time = time.time()
        self._last_odom_time = time.time()

        # Set initial mock health status
        self.system_health['battery']['voltage'] = 11.8
        self.system_health['battery']['percentage'] = 85.0
        self.system_health['battery']['status'] = 'ok'

        self.system_health['sensors']['lidar'] = 'ok'
        self.system_health['sensors']['imu'] = 'ok'
        self.system_health['sensors']['camera'] = 'ok'

        self.system_health['motors']['status'] = 'ok'
        self.system_health['motors']['left_wheel'] = 0.0
        self.system_health['motors']['right_wheel'] = 0.0

        self.system_health['navigation']['status'] = 'ok'
        self.system_health['navigation']['localization'] = 'ok'

        self.logger.info("Maintenance simulation mode initialized with mock sensor data")
            
    def start_monitoring(self) -> None:
        """Start health monitoring loop"""
        if self.is_monitoring:
            self.logger.warning("Monitoring already started")
            return
            
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        self.logger.info("Health monitoring started")
        
    def stop_monitoring(self) -> None:
        """Stop health monitoring"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5.0)
            
        self.logger.info("Health monitoring stopped")
        
    def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                # Perform health checks
                self._check_system_health()
                self._check_sensor_health()
                self._check_navigation_health()

                # Publish diagnostics
                if 'Node' in globals():
                    self._publish_diagnostics()

                # Log status
                self._log_health_status()

                # Sleep until next check
                time.sleep(self.health_check_interval)

            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5.0)  # Brief pause before retry

    def _generate_mock_sensor_data(self) -> None:
        """Generate mock sensor data for simulation mode"""
        import random

        # Simulate battery drain over time
        current_time = time.time()
        if hasattr(self, '_start_time'):
            elapsed = current_time - self._start_time
            # Battery drains slowly over time
            battery_level = max(20.0, 100.0 - (elapsed / 3600.0) * 10.0)  # 10% per hour
            self.system_health['battery']['percentage'] = battery_level
            self.system_health['battery']['voltage'] = 11.8 * (battery_level / 100.0)

            if battery_level < self.battery_threshold:
                self.system_health['battery']['status'] = 'low'
            else:
                self.system_health['battery']['status'] = 'ok'
        else:
            self._start_time = current_time

        # Simulate occasional sensor variations
        if random.random() < 0.1:  # 10% chance
            # Randomly vary sensor status
            sensors = ['lidar', 'imu', 'camera']
            sensor = random.choice(sensors)
            if random.random() < 0.8:  # 80% chance of being ok
                self.system_health['sensors'][sensor] = 'ok'
            else:
                self.system_health['sensors'][sensor] = 'warning'

        # Simulate motor activity
        if random.random() < 0.3:  # 30% chance of movement
            self.system_health['motors']['left_wheel'] = random.uniform(-0.5, 0.5)
            self.system_health['motors']['right_wheel'] = random.uniform(-0.5, 0.5)
        else:
            self.system_health['motors']['left_wheel'] = 0.0
            self.system_health['motors']['right_wheel'] = 0.0

        # Update timestamps
        self._last_battery_time = current_time
        self._last_lidar_time = current_time
        self._last_imu_time = current_time
        self._last_odom_time = current_time
                
    def _check_system_health(self) -> None:
        """Check system-level health metrics"""
        try:
            import psutil
            
            # CPU usage
            self.system_health['system']['cpu_usage'] = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.system_health['system']['memory_usage'] = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            self.system_health['system']['disk_usage'] = (disk.used / disk.total) * 100
            
        except ImportError:
            # Fallback if psutil not available
            self.system_health['system']['cpu_usage'] = 0.0
            self.system_health['system']['memory_usage'] = 0.0
            self.system_health['system']['disk_usage'] = 0.0
        except Exception as e:
            self.logger.error(f"Error checking system health: {e}")
            
    def _check_sensor_health(self) -> None:
        """Check sensor health status"""
        # In simulation, sensors are always healthy
        # In real deployment, this would check actual sensor data
        current_time = time.time()
        
        # Check if we've received recent sensor data
        if hasattr(self, '_last_battery_time'):
            if current_time - self._last_battery_time > 60:
                self.system_health['sensors']['battery'] = 'error'
            else:
                self.system_health['sensors']['battery'] = 'ok'
        else:
            self.system_health['sensors']['battery'] = 'unknown'
            
        if hasattr(self, '_last_lidar_time'):
            if current_time - self._last_lidar_time > 10:
                self.system_health['sensors']['lidar'] = 'error'
            else:
                self.system_health['sensors']['lidar'] = 'ok'
        else:
            self.system_health['sensors']['lidar'] = 'unknown'
            
        if hasattr(self, '_last_imu_time'):
            if current_time - self._last_imu_time > 10:
                self.system_health['sensors']['imu'] = 'error'
            else:
                self.system_health['sensors']['imu'] = 'ok'
        else:
            self.system_health['sensors']['imu'] = 'unknown'
            
    def _check_navigation_health(self) -> None:
        """Check navigation system health"""
        # Check if navigation stack is responsive
        current_time = time.time()
        
        if hasattr(self, '_last_odom_time'):
            if current_time - self._last_odom_time > 5:
                self.system_health['navigation']['status'] = 'error'
            else:
                self.system_health['navigation']['status'] = 'ok'
        else:
            self.system_health['navigation']['status'] = 'unknown'
            
    def _battery_callback(self, msg: BatteryState) -> None:
        """Battery status callback"""
        self._last_battery_time = time.time()
        self.system_health['battery']['voltage'] = msg.voltage
        self.system_health['battery']['percentage'] = msg.percentage
        
        if msg.percentage < self.battery_threshold:
            self.logger.warning(f"Low battery: {msg.percentage:.1f}%")
            self.system_health['battery']['status'] = 'low'
        else:
            self.system_health['battery']['status'] = 'ok'
            
    def _imu_callback(self, msg: Imu) -> None:
        """IMU data callback"""
        self._last_imu_time = time.time()
        
    def _lidar_callback(self, msg: LaserScan) -> None:
        """LIDAR scan callback"""
        self._last_lidar_time = time.time()
        
        # Check if LIDAR is providing valid data
        if len(msg.ranges) > 0 and not all(r == 0.0 for r in msg.ranges):
            self.system_health['sensors']['lidar'] = 'ok'
        else:
            self.system_health['sensors']['lidar'] = 'error'
            
    def _odom_callback(self, msg: Odometry) -> None:
        """Odometry callback"""
        self._last_odom_time = time.time()
        
    def _publish_diagnostics(self) -> None:
        """Publish diagnostic information"""
        try:
            diagnostic_msg = DiagnosticArray()
            diagnostic_msg.header = Header()
            diagnostic_msg.header.stamp = self.get_clock().now().to_msg()
            
            # Battery diagnostics
            battery_status = DiagnosticStatus()
            battery_status.name = "turtlebot3_battery"
            battery_status.hardware_id = "battery"
            battery_status.level = DiagnosticStatus.OK if self.system_health['battery']['status'] == 'ok' else DiagnosticStatus.WARN
            battery_status.message = f"Battery: {self.system_health['battery']['percentage']:.1f}%"
            diagnostic_msg.status.append(battery_status)
            
            # Sensor diagnostics
            for sensor, status in self.system_health['sensors'].items():
                sensor_status = DiagnosticStatus()
                sensor_status.name = f"turtlebot3_{sensor}"
                sensor_status.hardware_id = sensor
                sensor_status.level = DiagnosticStatus.OK if status == 'ok' else DiagnosticStatus.ERROR
                sensor_status.message = f"{sensor.capitalize()}: {status}"
                diagnostic_msg.status.append(sensor_status)
                
            self.diagnostic_pub.publish(diagnostic_msg)
            
        except Exception as e:
            self.logger.error(f"Error publishing diagnostics: {e}")
            
    def _log_health_status(self) -> None:
        """Log current health status"""
        battery = self.system_health['battery']
        sensors = self.system_health['sensors']
        system = self.system_health['system']
        
        self.logger.info(
            f"Health Status - Battery: {battery['percentage']:.1f}% ({battery['status']}), "
            f"Sensors: LIDAR={sensors['lidar']}, IMU={sensors['imu']}, "
            f"System: CPU={system['cpu_usage']:.1f}%, MEM={system['memory_usage']:.1f}%"
        )
        
    def is_healthy(self) -> bool:
        """Check if overall system is healthy"""
        # Check battery
        if self.system_health['battery']['status'] in ['low', 'error']:
            return False
            
        # Check critical sensors
        critical_sensors = ['lidar', 'imu']
        for sensor in critical_sensors:
            if self.system_health['sensors'][sensor] == 'error':
                return False
                
        # Check system resources
        system = self.system_health['system']
        if system['cpu_usage'] > 90 or system['memory_usage'] > 90:
            return False
            
        return True
        
    def get_health_report(self) -> Dict:
        """Get comprehensive health report"""
        return {
            'timestamp': time.time(),
            'healthy': self.is_healthy(),
            'battery': self.system_health['battery'],
            'sensors': self.system_health['sensors'],
            'motors': self.system_health['motors'],
            'navigation': self.system_health['navigation'],
            'system': self.system_health['system']
        }
        
    def run(self) -> None:
        """Run maintenance monitoring (blocking)"""
        self.start_monitoring()
        try:
            while rclpy.ok():
                rclpy.spin_once(self, timeout_sec=1.0)
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        finally:
            self.stop_monitoring()
            
    def shutdown(self) -> None:
        """Shutdown maintenance module"""
        self.logger.info("Shutting down maintenance automation")
        self.stop_monitoring()
        
        if 'Node' in globals():
            self.destroy_node()
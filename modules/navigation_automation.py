#!/usr/bin/env python3
"""
Navigation Automation Module for TurtleBot3
Handles SLAM, path planning, and autonomous navigation
Supports both simulation and hardware deployment
"""

import rclpy
import time
import threading
import logging
import math
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# ROS2 imports
try:
    from rclpy.node import Node
    from rclpy.action import ActionClient
    from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped, Twist
    from nav_msgs.msg import OccupancyGrid, Odometry, Path
    from sensor_msgs.msg import LaserScan
    from nav2_msgs.action import NavigateToPose, FollowWaypoints
    from nav2_msgs.srv import ManageLifecycleNodes
    from std_srvs.srv import Empty
except ImportError:
    # Fallback for systems without ROS2 installed
    Node = object
    ActionClient = object
    PoseStamped = object
    PoseWithCovarianceStamped = object
    Twist = object
    OccupancyGrid = object
    Odometry = object
    Path = object
    LaserScan = object
    NavigateToPose = object
    FollowWaypoints = object
    ManageLifecycleNodes = object
    Empty = object


class NavigationAutomation(Node if 'Node' in globals() else object):
    """Automates navigation, SLAM, and path planning for TurtleBot3"""
    
    def __init__(self, config: Dict, simulation_mode: bool = True):
        """
        Initialize navigation automation
        
        Args:
            config: Configuration dictionary
            simulation_mode: True for simulation, False for hardware
        """
        # Initialize ROS node if available
        if 'Node' in globals():
            super().__init__('navigation_automation')
            
        self.config = config
        self.simulation_mode = simulation_mode
        self.logger = logging.getLogger(__name__)
        
        # Navigation configuration
        nav_config = config.get('navigation', {})
        self.use_slam = nav_config.get('use_slam', True)
        self.localization = nav_config.get('localization', False)
        self.map_file = nav_config.get('map_file')
        
        # State tracking
        self.is_navigating = False
        self.navigation_active = False
        self.current_pose = None
        self.current_map = None
        self.goal_pose = None
        
        # ROS2 clients and subscribers
        self.nav_client = None
        self.waypoints_client = None
        self.pose_sub = None
        self.map_sub = None
        self.cmd_vel_pub = None
        self.initial_pose_pub = None
        
        # Navigation thread
        self.navigation_thread = None
        
    def initialize(self) -> bool:
        """Initialize navigation module"""
        try:
            self.logger.info("Initializing navigation automation module")

            if 'Node' in globals():
                self._setup_ros_connections()
                self.logger.info("ROS2 navigation connections established")
            else:
                self.logger.info("ROS2 not available, running navigation in simulation mode")
                self._start_simulation_mode()

            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize navigation module: {e}")
            return False
            
    def _setup_ros_connections(self) -> None:
        """Setup ROS2 action clients and subscribers"""
        try:
            # Navigation action client
            self.nav_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
            
            # Waypoints action client
            self.waypoints_client = ActionClient(self, FollowWaypoints, 'follow_waypoints')
            
            # Pose subscriber
            self.pose_sub = self.create_subscription(
                PoseWithCovarianceStamped,
                '/amcl_pose' if self.localization else '/odom',
                self._pose_callback,
                10
            )
            
            # Map subscriber
            self.map_sub = self.create_subscription(
                OccupancyGrid,
                '/map',
                self._map_callback,
                10
            )
            
            # Velocity publisher
            self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
            
            # Initial pose publisher
            self.initial_pose_pub = self.create_publisher(
                PoseWithCovarianceStamped,
                '/initialpose',
                10
            )
            
            self.logger.info("ROS2 navigation connections established")

        except Exception as e:
            self.logger.error(f"Failed to setup ROS navigation connections: {e}")

    def _start_simulation_mode(self) -> None:
        """Start navigation simulation mode"""
        self.logger.info("Navigation simulation mode initialized")
        self.logger.info("Mock navigation goals and pose tracking available")

        # Initialize mock pose
        self.current_pose = {
            'position': {'x': 0.0, 'y': 0.0, 'z': 0.0},
            'orientation': {'x': 0.0, 'y': 0.0, 'z': 0.0, 'w': 1.0}
        }
            
    def start_navigation(self) -> None:
        """Start navigation system"""
        if self.navigation_active:
            self.logger.warning("Navigation already active")
            return
            
        self.navigation_active = True
        self.logger.info("Navigation system started")
        
        # Start navigation thread
        self.navigation_thread = threading.Thread(target=self._navigation_loop, daemon=True)
        self.navigation_thread.start()
        
    def stop_navigation(self) -> None:
        """Stop navigation system"""
        self.navigation_active = False
        self.is_navigating = False
        
        if self.navigation_thread:
            self.navigation_thread.join(timeout=5.0)
            
        self.logger.info("Navigation system stopped")
        
    def _navigation_loop(self) -> None:
        """Main navigation loop"""
        while self.navigation_active:
            try:
                if 'Node' in globals():
                    rclpy.spin_once(self, timeout_sec=0.1)
                time.sleep(0.1)
            except Exception as e:
                self.logger.error(f"Error in navigation loop: {e}")
                time.sleep(1.0)
                
    def navigate_to_pose(self, x: float, y: float, yaw: float = 0.0) -> bool:
        """
        Navigate to specific pose
        
        Args:
            x: Target X coordinate
            y: Target Y coordinate
            yaw: Target yaw angle in radians
            
        Returns:
            True if navigation started successfully
        """
        if not 'Node' in globals():
            self.logger.warning("ROS2 not available, simulating navigation")
            return self._simulate_navigation(x, y, yaw)
            
        try:
            # Wait for navigation action server
            if not self.nav_client.wait_for_server(timeout_sec=10.0):
                self.logger.error("Navigation action server not available")
                return False
                
            # Create goal pose
            goal_msg = NavigateToPose.Goal()
            goal_msg.pose.header.frame_id = "map"
            goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
            
            goal_msg.pose.pose.position.x = x
            goal_msg.pose.pose.position.y = y
            
            # Convert yaw to quaternion
            goal_msg.pose.pose.orientation.z = math.sin(yaw / 2.0)
            goal_msg.pose.pose.orientation.w = math.cos(yaw / 2.0)
            
            # Send goal
            self.is_navigating = True
            self.goal_pose = (x, y, yaw)
            
            send_goal_future = self.nav_client.send_goal_async(goal_msg)
            send_goal_future.add_done_callback(self._navigate_to_pose_response)
            
            self.logger.info(f"Navigating to pose: x={x}, y={y}, yaw={yaw}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to navigate to pose: {e}")
            self.is_navigating = False
            return False
            
    def _simulate_navigation(self, x: float, y: float, yaw: float) -> bool:
        """Simulate navigation for testing without ROS2"""
        import threading

        self.logger.info(f"🚀 Starting navigation to pose: x={x:.2f}, y={y:.2f}, yaw={yaw:.2f} radians")

        # Calculate navigation parameters
        distance = math.sqrt(x**2 + y**2)
        nav_time = max(2.0, distance * 1.5)  # 1.5 seconds per meter, minimum 2 seconds

        self.logger.info(f"📏 Distance to target: {distance:.2f} meters")
        self.logger.info(f"⏱️  Estimated navigation time: {nav_time:.1f} seconds")

        self.is_navigating = True
        self.goal_pose = (x, y, yaw)

        # Start simulation in background thread
        nav_thread = threading.Thread(target=self._run_navigation_simulation, args=(x, y, yaw, nav_time))
        nav_thread.daemon = True
        nav_thread.start()

        self.logger.info("🎯 Navigation goal accepted - robot is moving...")
        return True

    def _run_navigation_simulation(self, target_x: float, target_y: float, target_yaw: float, duration: float) -> None:
        """Run detailed navigation simulation"""
        import random

        start_time = time.time()
        steps = int(duration / 0.5)  # Update every 0.5 seconds

        for step in range(steps):
            elapsed = time.time() - start_time
            progress = elapsed / duration

            if progress >= 1.0:
                break

            # Calculate current position (linear interpolation)
            current_x = target_x * progress
            current_y = target_y * progress
            current_yaw = target_yaw * progress

            # Add some realistic variation
            noise_x = random.uniform(-0.05, 0.05)
            noise_y = random.uniform(-0.05, 0.05)
            current_x += noise_x
            current_y += noise_y

            # Update mock pose
            if hasattr(self, 'current_pose') and self.current_pose:
                self.current_pose['position']['x'] = current_x
                self.current_pose['position']['y'] = current_y

            # Log progress
            if step % 4 == 0:  # Log every 2 seconds
                self.logger.info(f"📍 Navigation progress: {progress*100:.1f}% - Position: ({current_x:.2f}, {current_y:.2f})")

            time.sleep(0.5)

        # Navigation complete
        self.logger.info(f"✅ Navigation completed! Final position: ({target_x:.2f}, {target_y:.2f})")
        self.logger.info(f"🎯 Goal reached with {target_yaw:.2f} radian orientation")
        self.is_navigating = False
        
    def _navigate_to_pose_response(self, future) -> None:
        """Handle navigation response"""
        try:
            goal_handle = future.result()
            if not goal_handle.accepted:
                self.logger.error("Navigation goal rejected")
                self.is_navigating = False
                return
                
            self.logger.info("Navigation goal accepted")
            
            get_result_future = goal_handle.get_result_async()
            get_result_future.add_done_callback(self._navigate_to_pose_result)
            
        except Exception as e:
            self.logger.error(f"Error in navigation response: {e}")
            self.is_navigating = False
            
    def _navigate_to_pose_result(self, future) -> None:
        """Handle navigation result"""
        try:
            result = future.result().result
            if result:
                self.logger.info(f"Navigation completed: {result}")
            else:
                self.logger.warning("Navigation completed with no result")
        except Exception as e:
            self.logger.error(f"Error in navigation result: {e}")
        finally:
            self.is_navigating = False
            
    def follow_waypoints(self, waypoints: List[Tuple[float, float, float]]) -> bool:
        """
        Follow a series of waypoints
        
        Args:
            waypoints: List of (x, y, yaw) tuples
            
        Returns:
            True if waypoint following started successfully
        """
        if not 'Node' in globals():
            self.logger.warning("ROS2 not available, simulating waypoint following")
            return self._simulate_waypoints(waypoints)
            
        try:
            # Wait for waypoints action server
            if not self.waypoints_client.wait_for_server(timeout_sec=10.0):
                self.logger.error("Waypoints action server not available")
                return False
                
            # Create waypoints goal
            goal_msg = FollowWaypoints.Goal()
            goal_msg.poses = []
            
            for x, y, yaw in waypoints:
                pose = PoseStamped()
                pose.header.frame_id = "map"
                pose.header.stamp = self.get_clock().now().to_msg()
                pose.pose.position.x = x
                pose.pose.position.y = y
                pose.pose.orientation.z = math.sin(yaw / 2.0)
                pose.pose.orientation.w = math.cos(yaw / 2.0)
                goal_msg.poses.append(pose)
                
            # Send goal
            self.is_navigating = True
            send_goal_future = self.waypoints_client.send_goal_async(goal_msg)
            send_goal_future.add_done_callback(self._follow_waypoints_response)
            
            self.logger.info(f"Following {len(waypoints)} waypoints")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to follow waypoints: {e}")
            self.is_navigating = False
            return False
            
    def _simulate_waypoints(self, waypoints: List[Tuple[float, float, float]]) -> bool:
        """Simulate waypoint following"""
        self.logger.info(f"Simulating {len(waypoints)} waypoints")
        
        self.is_navigating = True
        for i, (x, y, yaw) in enumerate(waypoints):
            self.logger.info(f"Simulating waypoint {i+1}/{len(waypoints)}: ({x}, {y}, {yaw})")
            time.sleep(2.0)  # Simulate travel time
            
        self.is_navigating = False
        self.logger.info("Simulated waypoint following completed")
        return True
        
    def _follow_waypoints_response(self, future) -> None:
        """Handle waypoints response"""
        try:
            goal_handle = future.result()
            if not goal_handle.accepted:
                self.logger.error("Waypoints goal rejected")
                self.is_navigating = False
                return
                
            self.logger.info("Waypoints goal accepted")
            
            get_result_future = goal_handle.get_result_async()
            get_result_future.add_done_callback(self._follow_waypoints_result)
            
        except Exception as e:
            self.logger.error(f"Error in waypoints response: {e}")
            self.is_navigating = False
            
    def _follow_waypoints_result(self, future) -> None:
        """Handle waypoints result"""
        try:
            result = future.result().result
            if result:
                self.logger.info(f"Waypoints completed: {result}")
            else:
                self.logger.warning("Waypoints completed with no result")
        except Exception as e:
            self.logger.error(f"Error in waypoints result: {e}")
        finally:
            self.is_navigating = False
            
    def stop_robot(self) -> None:
        """Stop robot movement"""
        if 'Node' in globals() and self.cmd_vel_pub:
            twist = Twist()
            twist.linear.x = 0.0
            twist.angular.z = 0.0
            self.cmd_vel_pub.publish(twist)
            
        self.logger.info("Robot stopped")
        
    def set_initial_pose(self, x: float, y: float, yaw: float) -> None:
        """Set initial robot pose for localization"""
        if not 'Node' in globals() or not self.initial_pose_pub:
            self.logger.warning("Cannot set initial pose - ROS2 not available")
            return
            
        try:
            pose_msg = PoseWithCovarianceStamped()
            pose_msg.header.frame_id = "map"
            pose_msg.header.stamp = self.get_clock().now().to_msg()
            
            pose_msg.pose.pose.position.x = x
            pose_msg.pose.pose.position.y = y
            pose_msg.pose.pose.orientation.z = math.sin(yaw / 2.0)
            pose_msg.pose.pose.orientation.w = math.cos(yaw / 2.0)
            
            self.initial_pose_pub.publish(pose_msg)
            self.logger.info(f"Initial pose set: ({x}, {y}, {yaw})")
            
        except Exception as e:
            self.logger.error(f"Failed to set initial pose: {e}")
            
    def _pose_callback(self, msg: PoseWithCovarianceStamped) -> None:
        """Handle pose updates"""
        self.current_pose = msg
        
    def _map_callback(self, msg: OccupancyGrid) -> None:
        """Handle map updates"""
        self.current_map = msg
        
    def get_current_pose(self) -> Optional[PoseWithCovarianceStamped]:
        """Get current robot pose"""
        return self.current_pose
        
    def get_current_map(self) -> Optional[OccupancyGrid]:
        """Get current occupancy grid map"""
        return self.current_map
        
    def is_navigation_active(self) -> bool:
        """Check if navigation is currently active"""
        return self.is_navigating
        
    def run(self) -> None:
        """Run navigation system (blocking)"""
        self.start_navigation()
        try:
            while rclpy.ok():
                rclpy.spin_once(self, timeout_sec=1.0)
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        finally:
            self.stop_navigation()
            
    def shutdown(self) -> None:
        """Shutdown navigation module"""
        self.logger.info("Shutting down navigation automation")
        self.stop_navigation()
        self.stop_robot()
        
        if 'Node' in globals():
            self.destroy_node()
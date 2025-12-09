#!/usr/bin/env python3
"""
Setup Automation Module for TurtleBot3
Handles ROS2 and TurtleBot3 installation, configuration, and workspace setup
Supports both simulation and hardware deployment
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional


class SetupAutomation:
    """Automates ROS2 and TurtleBot3 setup and configuration"""
    
    def __init__(self, config: Dict, simulation_mode: bool = True):
        """
        Initialize setup automation
        
        Args:
            config: Configuration dictionary
            simulation_mode: True for simulation setup, False for hardware
        """
        self.config = config
        self.simulation_mode = simulation_mode
        self.logger = logging.getLogger(__name__)
        
        # Setup paths
        self.workspace_path = Path.home() / "turtlebot3_ws"
        self.ros_distro = self._detect_ros_distro()
        
    def _detect_ros_distro(self) -> str:
        """Detect installed ROS2 distribution"""
        try:
            result = subprocess.run(
                ["rosversion", "-d"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            if result.returncode == 0:
                distro = result.stdout.strip()
                self.logger.info(f"Detected ROS2 distribution: {distro}")
                return distro
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
            
        # Default to humble for Ubuntu 22.04
        self.logger.warning("Could not detect ROS2 distro, defaulting to humble")
        return "humble"
        
    def initialize(self) -> bool:
        """Initialize setup module"""
        try:
            self.logger.info("Initializing setup automation module")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize setup module: {e}")
            return False
            
    def needs_setup(self) -> bool:
        """Check if setup is needed"""
        # Check if workspace exists
        if not self.workspace_path.exists():
            return True
            
        # Check if key packages are installed
        required_packages = self._get_required_packages()
        for package in required_packages:
            if not self._is_package_installed(package):
                return True
                
        return False
        
    def run_setup(self) -> bool:
        """Run complete setup process"""
        try:
            self.logger.info("Starting TurtleBot3 setup automation...")
            
            # Step 1: Update system packages
            if not self._update_system():
                return False
                
            # Step 2: Install ROS2 packages
            if not self._install_ros2_packages():
                return False
                
            # Step 3: Install TurtleBot3 packages
            if not self._install_turtlebot3_packages():
                return False
                
            # Step 4: Create ROS workspace
            if not self._create_workspace():
                return False
                
            # Step 5: Setup environment
            if not self._setup_environment():
                return False
                
            # Step 6: Verify setup
            if not self._verify_setup():
                return False
                
            self.logger.info("TurtleBot3 setup completed successfully!")
            return True
            
        except Exception as e:
            self.logger.error(f"Setup failed: {e}")
            return False
            
    def _get_required_packages(self) -> List[str]:
        """Get list of required ROS2 packages"""
        base_packages = [
            f"ros-{self.ros_distro}-desktop",
            f"ros-{self.ros_distro}-navigation2",
            f"ros-{self.ros_distro}-nav2-bringup",
            f"ros-{self.ros_distro}-nav2-costmap-2d",
            f"ros-{self.ros_distro}-nav2-planner",
            f"ros-{self.ros_distro}-nav2-controller",
            f"ros-{self.ros_distro}-nav2-recoveries",
            f"ros-{self.ros_distro}-nav2-bt-navigator",
            f"ros-{self.ros_distro}-nav2-lifecycle-manager",
            f"ros-{self.ros_distro}-robot-localization",
            f"ros-{self.ros_distro}-slam-toolbox",
        ]
        
        turtlebot3_packages = [
            f"ros-{self.ros_distro}-turtlebot3",
            f"ros-{self.ros_distro}-turtlebot3-msgs",
            f"ros-{self.ros_distro}-turtlebot3-simulations",
        ]
        
        if self.simulation_mode:
            simulation_packages = [
                f"ros-{self.ros_distro}-gazebo-ros-pkgs",
                f"ros-{self.ros_distro}-gazebo-ros2-control",
                f"ros-{self.ros_distro}-ros-gz-sim",
                f"ros-{self.ros_distro}-ros-gz-bridge",
                f"ros-{self.ros_distro}-ros-gz-image",
                f"ros-{self.ros_distro}-turtlebot3-gazebo",
                f"ros-{self.ros_distro}-turtlebot3-simulations",
                f"ros-{self.ros_distro}-aws-robomaker-small-warehouse-world",
            ]
            return base_packages + turtlebot3_packages + simulation_packages
        else:
            hardware_packages = [
                f"ros-{self.ros_distro}-turtlebot3-bringup",
                f"ros-{self.ros_distro}-hls-lfcd-lds-driver",
                f"ros-{self.ros_distro}-turtlebot3-teleop",
            ]
            return base_packages + turtlebot3_packages + hardware_packages
            
    def _update_system(self) -> bool:
        """Update system packages"""
        try:
            self.logger.info("Updating system packages...")
            result = subprocess.run(
                ["sudo", "apt", "update"],
                check=True,
                capture_output=True,
                text=True
            )
            self.logger.info("System packages updated successfully")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to update system: {e}")
            return False
            
    def _install_ros2_packages(self) -> bool:
        """Install ROS2 packages"""
        try:
            self.logger.info("Installing ROS2 packages...")
            packages = [
                f"ros-{self.ros_distro}-desktop",
                f"ros-{self.ros_distro}-navigation2",
                f"ros-{self.ros_distro}-nav2-bringup",
            ]
            
            cmd = ["sudo", "apt", "install", "-y"] + packages
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            self.logger.info("ROS2 packages installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to install ROS2 packages: {e}")
            return False
            
    def _install_turtlebot3_packages(self) -> bool:
        """Install TurtleBot3 packages"""
        try:
            self.logger.info("Installing TurtleBot3 packages...")
            
            if self.simulation_mode:
                packages = [
                    f"ros-{self.ros_distro}-turtlebot3*",
                    f"ros-{self.ros_distro}-gazebo-ros-pkgs",
                    f"ros-{self.ros_distro}-ros-gz*",
                ]
            else:
                packages = [
                    f"ros-{self.ros_distro}-turtlebot3*",
                    f"ros-{self.ros_distro}-hls-lfcd-lds-driver",
                ]
                
            cmd = ["sudo", "apt", "install", "-y"] + packages
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            self.logger.info("TurtleBot3 packages installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to install TurtleBot3 packages: {e}")
            return False
            
    def _create_workspace(self) -> bool:
        """Create and build ROS workspace"""
        try:
            self.logger.info("Creating ROS workspace...")
            
            # Create workspace directory
            self.workspace_path.mkdir(parents=True, exist_ok=True)
            src_path = self.workspace_path / "src"
            src_path.mkdir(exist_ok=True)
            
            # Initialize workspace if empty
            if not any(src_path.iterdir()):
                self.logger.info("Initializing empty workspace...")
                
            # Build workspace
            self.logger.info("Building workspace...")
            os.chdir(self.workspace_path)
            
            result = subprocess.run(
                ["colcon", "build", "--symlink-install"],
                check=True,
                capture_output=True,
                text=True
            )
            
            self.logger.info("ROS workspace created and built successfully")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to create workspace: {e}")
            return False
            
    def _setup_environment(self) -> bool:
        """Setup environment variables"""
        try:
            self.logger.info("Setting up environment...")
            
            # Set TurtleBot3 model
            model = self.config.get('simulation', {}).get('robot_model', 'waffle')
            os.environ['TURTLEBOT3_MODEL'] = model
            
            if self.simulation_mode:
                # Set Gazebo model path
                gazebo_path = f"/opt/ros/{self.ros_distro}/share/turtlebot3_gazebo/models"
                current_path = os.environ.get('GAZEBO_MODEL_PATH', '')
                if gazebo_path not in current_path:
                    os.environ['GAZEBO_MODEL_PATH'] = f"{current_path}:{gazebo_path}"
                    
            # Add workspace setup to bashrc if not already present
            bashrc_path = Path.home() / ".bashrc"
            setup_line = f"source {self.workspace_path}/install/setup.bash"
            
            if bashrc_path.exists():
                bashrc_content = bashrc_path.read_text()
                if setup_line not in bashrc_content:
                    with open(bashrc_path, 'a') as f:
                        f.write(f"\n# TurtleBot3 Automation\n{setup_line}\n")
                        
            self.logger.info("Environment setup completed")
            return True
        except Exception as e:
            self.logger.error(f"Failed to setup environment: {e}")
            return False
            
    def _verify_setup(self) -> bool:
        """Verify that setup was successful"""
        try:
            self.logger.info("Verifying setup...")
            
            # Check if workspace exists
            if not self.workspace_path.exists():
                self.logger.error("Workspace directory not found")
                return False
                
            # Check if install directory exists
            install_path = self.workspace_path / "install"
            if not install_path.exists():
                self.logger.error("Workspace not built")
                return False
                
            # Check if key packages are available
            required_packages = self._get_required_packages()[:5]  # Check first 5
            for package in required_packages:
                if not self._is_package_installed(package):
                    self.logger.warning(f"Package {package} may not be properly installed")
                    
            self.logger.info("Setup verification completed")
            return True
        except Exception as e:
            self.logger.error(f"Setup verification failed: {e}")
            return False
            
    def _is_package_installed(self, package_name: str) -> bool:
        """Check if a ROS package is installed"""
        try:
            result = subprocess.run(
                ["dpkg", "-l", package_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
            
    def shutdown(self) -> None:
        """Shutdown setup module"""
        self.logger.info("Setup automation module shutdown")
        
    def get_workspace_path(self) -> Path:
        """Get ROS workspace path"""
        return self.workspace_path
        
    def get_ros_distro(self) -> str:
        """Get ROS2 distribution"""
        return self.ros_distro
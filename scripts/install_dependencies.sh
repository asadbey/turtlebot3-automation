#!/usr/bin/env python3
"""
Installation script for TurtleBot3 automation dependencies
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {version.major}.{version.minor} detected")
    return True


def install_system_dependencies():
    """Install system-level dependencies"""
    commands = [
        ("sudo apt update", "Updating package lists"),
        ("sudo apt install -y python3-pip python3-venv", "Installing Python tools"),
        ("sudo apt install -y portaudio19-dev", "Installing audio dependencies"),
        ("sudo apt install -y pkg-config", "Installing build tools"),
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    return True


def install_python_dependencies():
    """Install Python dependencies"""
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False
        
    return run_command(
        f"pip install -r {requirements_file}",
        "Installing Python dependencies"
    )


def setup_ros_environment():
    """Setup ROS2 environment variables"""
    ros_distro = os.environ.get('ROS_DISTRO', 'humble')
    
    # Add to bashrc if not already present
    bashrc_path = Path.home() / ".bashrc"
    setup_lines = [
        f"source /opt/ros/{ros_distro}/setup.bash",
        "export TURTLEBOT3_MODEL=waffle",
    ]
    
    if bashrc_path.exists():
        bashrc_content = bashrc_path.read_text()
        for line in setup_lines:
            if line not in bashrc_content:
                with open(bashrc_path, 'a') as f:
                    f.write(f"\n# TurtleBot3 Automation\n{line}\n")
    
    print("✅ ROS2 environment configured")
    return True


def create_directories():
    """Create necessary directories"""
    directories = [
        Path.home() / "turtlebot3_ws",
        Path.home() / "turtlebot3_ws/src",
        Path("logs"),
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    
    print("✅ Directories created")
    return True


def main():
    """Main installation function"""
    print("🚀 TurtleBot3 Automation Installation")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install system dependencies
    if not install_system_dependencies():
        print("❌ System dependency installation failed")
        sys.exit(1)
    
    # Install Python dependencies
    if not install_python_dependencies():
        print("❌ Python dependency installation failed")
        sys.exit(1)
    
    # Setup ROS environment
    if not setup_ros_environment():
        print("❌ ROS environment setup failed")
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        print("❌ Directory creation failed")
        sys.exit(1)
    
    print("\n🎉 Installation completed successfully!")
    print("\nNext steps:")
    print("1. Source your ROS2 environment: source ~/.bashrc")
    print("2. Run the automation: python turtlebot_automation.py")
    print("3. For simulation mode: python turtlebot_automation.py --module setup")


if __name__ == "__main__":
    main()
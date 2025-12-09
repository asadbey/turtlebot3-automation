# Installation Guide

This guide provides step-by-step instructions for installing and setting up the TurtleBot3 automation system.

## Table of Contents

- [System Requirements](#system-requirements)
- [Prerequisites](#prerequisites)
- [Installation Steps](#installation-steps)
- [Configuration](#configuration)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

## System Requirements

### Hardware Requirements

**Minimum Requirements:**
- CPU: Intel i5 or AMD Ryzen 5 (or equivalent)
- RAM: 4GB (8GB recommended)
- Storage: 10GB free space
- USB Port: For TurtleBot3 hardware (optional)

**Recommended Requirements:**
- CPU: Intel i7 or AMD Ryzen 7 (or equivalent)
- RAM: 16GB or higher
- Storage: 20GB free space (SSD recommended)
- GPU: NVIDIA GPU with CUDA support (for object detection)

### Software Requirements

**Operating System:**
- Ubuntu 20.04 LTS (Focal Fossa) - For ROS2 Foxy
- Ubuntu 22.04 LTS (Jammy Jellyfish) - For ROS2 Humble (Recommended)

**Python:**
- Python 3.8 or higher
- pip package manager

**Optional:**
- Docker 20.10+ (for containerized deployment)
- Git (for version control)

## Prerequisites

### 1. Update System Packages

```bash
sudo apt update
sudo apt upgrade -y
```

### 2. Install Basic Development Tools

```bash
sudo apt install -y \
    curl \
    wget \
    git \
    build-essential \
    cmake \
    python3-pip \
    python3-venv \
    software-properties-common
```

### 3. Install Audio Dependencies (for Voice Control)

```bash
sudo apt install -y \
    portaudio19-dev \
    python3-dev \
    gcc \
    make
```

### 4. Install System Monitoring Tools

```bash
sudo apt install -y \
    htop \
    iotop \
    nethogs
```

## Installation Steps

### Option 1: Automated Installation (Recommended)

Use the provided installation script for automated setup:

```bash
# Clone the repository
git clone https://github.com/yourusername/turtlebot-automation.git
cd turtlebot-automation

# Run automated installation
./scripts/install_dependencies.sh
```

### Option 2: Manual Installation

#### Step 1: Install ROS2

**For Ubuntu 22.04 (ROS2 Humble):**

```bash
# Set locale
sudo apt update && sudo apt install -y locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

# Add ROS2 apt repository
sudo apt install -y software-properties-common
sudo add-apt-repository universe
sudo apt update && sudo apt install -y curl gnupg lsb-release
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | sudo apt-key add -
sudo sh -c 'echo "deb [arch=$(dpkg --print-architecture)] http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" > /etc/apt/sources.list.d/ros2-latest.list'

# Install ROS2 Humble
sudo apt update
sudo apt install -y ros-humble-desktop
```

**For Ubuntu 20.04 (ROS2 Foxy):**

```bash
# Add ROS2 apt repository
sudo apt update && sudo apt install -y curl gnupg2 lsb-release
curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | sudo apt-key add -
sudo sh -c 'echo "deb [arch=$(dpkg --print-architecture)] http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" > /etc/apt/sources.list.d/ros2-latest.list'

# Install ROS2 Foxy
sudo apt update
sudo apt install -y ros-foxy-desktop
```

#### Step 2: Install TurtleBot3 Packages

```bash
# For ROS2 Humble
sudo apt install -y ros-humble-turtlebot3*

# For ROS2 Foxy  
sudo apt install -y ros-foxy-turtlebot3*
```

#### Step 3: Install Navigation Stack

```bash
# For ROS2 Humble
sudo apt install -y ros-humble-navigation2 ros-humble-nav2-bringup

# For ROS2 Foxy
sudo apt install -y ros-foxy-navigation2 ros-foxy-nav2-bringup
```

#### Step 4: Install Simulation Dependencies

```bash
# For ROS2 Humble
sudo apt install -y \
    ros-humble-gazebo-ros-pkgs \
    ros-humble-ros-gz-sim \
    ros-humble-ros-gz-bridge \
    ros-humble-ros-gz-image

# For ROS2 Foxy
sudo apt install -y \
    ros-foxy-gazebo-ros-pkgs \
    ros-foxy-gazebo-ros2-control
```

#### Step 5: Install Python Dependencies

```bash
# Install from requirements file
pip install -r requirements.txt

# Or install manually
pip install \
    rclpy \
    geometry-msgs \
    sensor-msgs \
    nav-msgs \
    vision-msgs \
    diagnostic-msgs \
    nav2-msgs \
    tf2-msgs \
    tf2-ros \
    cv-bridge \
    opencv-python \
    ultralytics \
    torch \
    torchvision \
    SpeechRecognition \
    gtts \
    playsound \
    pyaudio \
    psutil \
    PyYAML \
    numpy
```

#### Step 6: Setup ROS2 Environment

```bash
# Add to bashrc
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
echo "export TURTLEBOT3_MODEL=waffle" >> ~/.bashrc

# Apply to current session
source /opt/ros/humble/setup.bash
export TURTLEBOT3_MODEL=waffle
```

#### Step 7: Create ROS Workspace

```bash
# Create workspace directory
mkdir -p ~/turtlebot3_ws/src
cd ~/turtlebot3_ws

# Build workspace
colcon build

# Source workspace
echo "source ~/turtlebot3_ws/install/setup.bash" >> ~/.bashrc
source ~/turtlebot3_ws/install/setup.bash
```

## Configuration

### 1. Environment Variables

Set required environment variables:

```bash
# ROS2 Distribution
export ROS_DISTRO=humble

# TurtleBot3 Model
export TURTLEBOT3_MODEL=waffle  # Options: burger, waffle, waffle_pi

# Gazebo Model Path (for simulation)
export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:/opt/ros/humble/share/turtlebot3_gazebo/models

# ROS Domain ID (optional, for multi-robot setups)
export ROS_DOMAIN_ID=0
```

### 2. Audio Configuration (for Voice Control)

Test microphone setup:

```bash
# List available microphones
python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"

# Test audio recording
python -c "
import speech_recognition as sr
r = sr.Recognizer()
with sr.Microphone() as source:
    print('Say something!')
    audio = r.listen(source)
    print('You said: ' + r.recognize_google(audio))
"
```

### 3. GPU Configuration (for Object Detection)

If you have an NVIDIA GPU:

```bash
# Install CUDA Toolkit (Ubuntu 22.04)
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-ubuntu2204.pin
sudo mv cuda-ubuntu2204.pin /etc/apt/preferences.d/
wget https://developer.download.nvidia.com/compute/cuda/12.2.0/local_installers/cuda-repo-ubuntu2204-12-2-local_12.2.0-525.60.13-1_amd64.deb
sudo dpkg -i cuda-repo-ubuntu2204-12-2-local_12.2.0-525.60.13-1_amd64.deb
sudo cp /var/cuda-repo-ubuntu2204-12-2-local/cuda-*-keyring.gpg /usr/share/keyrings/
sudo apt-get update
sudo apt-get -y install cuda-toolkit-12-2

# Install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## Verification

### 1. Test ROS2 Installation

```bash
# Source ROS2
source /opt/ros/humble/setup.bash

# Test ROS2
ros2 topic list
ros2 node list
```

### 2. Test TurtleBot3 Packages

```bash
# Test TurtleBot3 simulation
ros2 run turtlebot3_gazebo turtlebot3_world

# In another terminal, test teleop
ros2 run turtlebot3_teleop teleop_keyboard
```

### 3. Test Python Dependencies

```bash
# Test imports
python -c "
import rclpy
import cv2
import torch
import ultralytics
import speech_recognition
print('All dependencies imported successfully!')
"
```

### 4. Test Automation System

```bash
# Test individual modules
python turtlebot_automation.py --module setup
python turtlebot_automation.py --module maintenance

# Test full system (simulation)
python turtlebot_automation.py
```

## Troubleshooting

### Common Issues

#### 1. ROS2 Not Found

**Problem:** `bash: ros2: command not found`

**Solution:**
```bash
# Source ROS2 environment
source /opt/ros/humble/setup.bash

# Add to bashrc permanently
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
```

#### 2. TurtleBot3 Model Not Set

**Problem:** `TURTLEBOT3_MODEL not set`

**Solution:**
```bash
export TURTLEBOT3_MODEL=waffle
echo "export TURTLEBOT3_MODEL=waffle" >> ~/.bashrc
```

#### 3. Gazebo Model Path Issues

**Problem:** Gazebo models not found

**Solution:**
```bash
export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:/opt/ros/humble/share/turtlebot3_gazebo/models
echo "export GAZEBO_MODEL_PATH=\$GAZEBO_MODEL_PATH:/opt/ros/humble/share/turtlebot3_gazebo/models" >> ~/.bashrc
```

#### 4. Python Import Errors

**Problem:** ModuleNotFoundError for Python packages

**Solution:**
```bash
# Reinstall Python dependencies
pip install -r requirements.txt --force-reinstall

# Check Python path
python -c "import sys; print(sys.path)"
```

#### 5. Audio/Microphone Issues

**Problem:** Microphone not working or permission denied

**Solution:**
```bash
# Check microphone permissions
ls -l /dev/snd/

# Add user to audio group
sudo usermod -a -G audio $USER

# Reboot or logout/login
sudo reboot
```

#### 6. CUDA/GPU Issues

**Problem:** PyTorch not using GPU

**Solution:**
```bash
# Check CUDA installation
nvcc --version
nvidia-smi

# Verify PyTorch CUDA support
python -c "
import torch
print(f'CUDA available: {torch.cuda.is_available()}')
print(f'CUDA device count: {torch.cuda.device_count()}')
"
```

### Performance Optimization

#### 1. System Performance

```bash
# Monitor system resources
htop
iotop

# Check ROS2 performance
ros2 topic hz /scan
ros2 topic bw /camera/image_raw
```

#### 2. Object Detection Optimization

```bash
# Test YOLOv8 performance
python -c "
from ultralytics import YOLO
import time

model = YOLO('yolov8n.pt')
start_time = time.time()
results = model('test.jpg')
end_time = time.time()
print(f'Inference time: {end_time - start_time:.3f}s')
"
```

### Getting Help

If you encounter issues:

1. **Check Logs**: Look at `turtlebot_automation.log` for error messages
2. **Verify Installation**: Run through the verification steps above
3. **Check Dependencies**: Ensure all required packages are installed
4. **Search Issues**: Check GitHub issues for similar problems
5. **Create Issue**: If the problem persists, create a detailed issue report

### Issue Report Template

When reporting issues, include:

```markdown
## Environment
- OS: Ubuntu 22.04/20.04
- ROS2 Version: Humble/Foxy
- Python Version: 3.x.x
- Hardware: CPU/RAM/GPU

## Problem Description
[Detailed description of the issue]

## Steps to Reproduce
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Error Messages
[Include full error output]

## What You Tried
[Include troubleshooting steps attempted]
```

## Next Steps

After successful installation:

1. **Read the User Manual**: `docs/user_manual.md`
2. **Review API Reference**: `docs/api_reference.md`
3. **Try Examples**: `docs/examples.md`
4. **Start with Simulation**: Begin with simulation before hardware
5. **Join Community**: Participate in discussions and contribute

## Advanced Installation

### Docker Installation

For containerized deployment:

```bash
# Build Docker image
docker build -t turtlebot-automation .

# Run container
docker run -it --rm \
    --gpus all \
    --device /dev/snd \
    -v $(pwd):/workspace \
    turtlebot-automation
```

### Development Installation

For developers contributing to the project:

```bash
# Clone with development dependencies
git clone https://github.com/yourusername/turtlebot-automation.git
cd turtlebot-automation

# Install development dependencies
pip install -r requirements-dev.txt

# Install in development mode
pip install -e .

# Run tests
python -m pytest tests/
```

This completes the installation process. Your TurtleBot3 automation system should now be ready to use!
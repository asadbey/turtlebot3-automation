#!/usr/bin/env python3
"""
Voice Control Module for TurtleBot3
Handles speech recognition and voice commands for robot control
Custom feature for the automation system
"""

import rclpy
import time
import threading
import logging
import re
from typing import Dict, List, Optional, Callable
from pathlib import Path

# ROS2 imports
try:
    from rclpy.node import Node
    from std_msgs.msg import String
    from geometry_msgs.msg import Twist
except ImportError:
    # Fallback for systems without ROS2 installed
    Node = object
    String = object
    Twist = object

# Voice recognition imports
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    sr = None

# Text-to-speech imports
try:
    import gtts
    from playsound import playsound
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    gtts = None
    playsound = None


class VoiceControl(Node if 'Node' in globals() else object):
    """Handles voice control for TurtleBot3"""
    
    def __init__(self, config: Dict):
        """
        Initialize voice control
        
        Args:
            config: Configuration dictionary
        """
        # Initialize ROS node if available
        if 'Node' in globals():
            super().__init__('voice_control')
            
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Voice configuration
        voice_config = config.get('voice', {})
        self.recognition_engine = voice_config.get('recognition_engine', 'google')
        self.tts_engine = voice_config.get('tts_engine', 'gtts')
        self.wake_word = voice_config.get('wake_word', 'turtlebot')
        
        # State tracking
        self.is_listening = False
        self.voice_active = False
        self.recognizer = None
        self.microphone = None
        
        # ROS2 publishers
        self.cmd_vel_pub = None
        self.voice_command_pub = None
        
        # Voice control thread
        self.voice_thread = None
        
        # Command patterns
        self.command_patterns = {
            'move_forward': r'(move|go).*(forward|ahead)',
            'move_backward': r'(move|go).*(back|backward)',
            'turn_left': r'(turn|rotate).*(left)',
            'turn_right': r'(turn|rotate).*(right)',
            'stop': r'stop',
            'navigate_to': r'(navigate|go to).*(\w+)',
            'explore': r'explore',
            'what_do_you_see': r'(what|tell me).*(you see|detect)',
            'follow_me': r'follow me',
            'emergency_stop': r'(emergency|stop).*(now|emergency)'
        }
        
        # Navigation locations (can be extended)
        self.locations = {
            'kitchen': (3.0, 2.0, 0.0),
            'living': (1.0, 1.0, 1.57),
            'bedroom': (2.0, 3.0, -1.57),
            'entrance': (0.0, 0.0, 0.0),
            'home': (0.0, 0.0, 0.0)
        }
        
    def initialize(self) -> bool:
        """Initialize voice control module"""
        try:
            self.logger.info("Initializing voice control module")
            
            # Check speech recognition availability
            if not SPEECH_RECOGNITION_AVAILABLE:
                self.logger.error("Speech recognition not available. Install with: pip install SpeechRecognition")
                return False
                
            # Initialize speech recognizer
            if not self._initialize_speech_recognition():
                return False
                
            # Setup ROS connections if available
            if 'Node' in globals():
                self._setup_ros_connections()
            else:
                self.logger.warning("ROS2 not available, running in simulation mode")
                
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize voice control: {e}")
            return False
            
    def _initialize_speech_recognition(self) -> bool:
        """Initialize speech recognition components"""
        try:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            
            # Adjust for ambient noise
            with self.microphone as source:
                self.logger.info("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                
            self.logger.info("Speech recognition initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize speech recognition: {e}")
            return False
            
    def _setup_ros_connections(self) -> None:
        """Setup ROS2 publishers"""
        try:
            # Velocity publisher
            self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
            
            # Voice command publisher
            self.voice_command_pub = self.create_publisher(String, '/voice_commands', 10)
            
            self.logger.info("ROS2 voice control connections established")
            
        except Exception as e:
            self.logger.error(f"Failed to setup ROS voice connections: {e}")
            
    def start_voice_control(self) -> None:
        """Start voice control system"""
        if self.voice_active:
            self.logger.warning("Voice control already active")
            return
            
        self.voice_active = True
        self.logger.info("Voice control system started")
        
        # Start voice control thread
        self.voice_thread = threading.Thread(target=self._voice_control_loop, daemon=True)
        self.voice_thread.start()
        
        # Provide voice feedback
        self.speak("Voice control activated. Say 'turtlebot' followed by a command.")
        
    def stop_voice_control(self) -> None:
        """Stop voice control system"""
        self.voice_active = False
        self.is_listening = False
        
        if self.voice_thread:
            self.voice_thread.join(timeout=5.0)
            
        self.logger.info("Voice control system stopped")
        
    def _voice_control_loop(self) -> None:
        """Main voice control loop"""
        while self.voice_active:
            try:
                # Listen for wake word
                if self._listen_for_wake_word():
                    self.speak("I'm listening")
                    
                    # Listen for command
                    command = self._listen_for_command()
                    if command:
                        self.logger.info(f"Voice command received: {command}")
                        
                        # Process command
                        self._process_voice_command(command)
                        
                time.sleep(0.1)  # Brief pause between listening cycles
                
            except Exception as e:
                self.logger.error(f"Error in voice control loop: {e}")
                time.sleep(1.0)
                
    def _listen_for_wake_word(self) -> bool:
        """Listen for wake word"""
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
                
            try:
                text = self.recognizer.recognize_google(audio).lower()
                return self.wake_word in text
                
            except sr.UnknownValueError:
                return False
                
        except sr.WaitTimeoutError:
            return False
        except Exception as e:
            self.logger.error(f"Error listening for wake word: {e}")
            return False
            
    def _listen_for_command(self) -> Optional[str]:
        """Listen for voice command"""
        try:
            self.is_listening = True
            
            with self.microphone as source:
                self.logger.info("Listening for command...")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
            try:
                # Try Google speech recognition first
                text = self.recognizer.recognize_google(audio).lower()
                self.logger.info(f"Recognized: {text}")
                return text
                
            except sr.UnknownValueError:
                self.logger.warning("Could not understand audio")
                return None
                
        except sr.WaitTimeoutError:
            self.logger.warning("Listening timeout")
            return None
        except Exception as e:
            self.logger.error(f"Error listening for command: {e}")
            return None
        finally:
            self.is_listening = False
            
    def _process_voice_command(self, command: str) -> None:
        """Process voice command and execute corresponding action"""
        try:
            # Publish command to ROS topic
            if self.voice_command_pub:
                cmd_msg = String()
                cmd_msg.data = command
                self.voice_command_pub.publish(cmd_msg)
                
            # Check command patterns
            if self._match_pattern(command, 'move_forward'):
                self._execute_movement('forward', 0.5, 0.0)
                
            elif self._match_pattern(command, 'move_backward'):
                self._execute_movement('backward', -0.5, 0.0)
                
            elif self._match_pattern(command, 'turn_left'):
                self._execute_movement('left', 0.0, 0.5)
                
            elif self._match_pattern(command, 'turn_right'):
                self._execute_movement('right', 0.0, -0.5)
                
            elif self._match_pattern(command, 'stop'):
                self._execute_movement('stop', 0.0, 0.0)
                
            elif self._match_pattern(command, 'navigate_to'):
                location = self._extract_location(command)
                if location:
                    self._execute_navigation(location)
                else:
                    self.speak("I don't know that location")
                    
            elif self._match_pattern(command, 'explore'):
                self._execute_exploration()
                
            elif self._match_pattern(command, 'what_do_you_see'):
                self._execute_object_detection()
                
            elif self._match_pattern(command, 'follow_me'):
                self._execute_follow_me()
                
            elif self._match_pattern(command, 'emergency_stop'):
                self._execute_emergency_stop()
                
            else:
                self.speak("I didn't understand that command")
                
        except Exception as e:
            self.logger.error(f"Error processing voice command: {e}")
            
    def _match_pattern(self, command: str, pattern_name: str) -> bool:
        """Check if command matches a pattern"""
        pattern = self.command_patterns.get(pattern_name, '')
        return bool(re.search(pattern, command, re.IGNORECASE))
        
    def _extract_location(self, command: str) -> Optional[str]:
        """Extract location from navigation command"""
        for location in self.locations.keys():
            if location in command:
                return location
        return None
        
    def _execute_movement(self, direction: str, linear: float, angular: float) -> None:
        """Execute movement command"""
        if 'Node' in globals() and self.cmd_vel_pub:
            twist = Twist()
            twist.linear.x = linear
            twist.angular.z = angular
            self.cmd_vel_pub.publish(twist)
            
        # Provide feedback
        if direction == 'stop':
            self.speak("Stopping")
        elif direction == 'emergency_stop':
            self.speak("Emergency stop activated")
        else:
            self.speak(f"Moving {direction}")
            
        # Stop after a short duration for movement commands
        if direction in ['forward', 'backward', 'left', 'right']:
            time.sleep(2.0)
            if self.cmd_vel_pub:
                twist = Twist()
                twist.linear.x = 0.0
                twist.angular.z = 0.0
                self.cmd_vel_pub.publish(twist)
                
    def _execute_navigation(self, location: str) -> None:
        """Execute navigation to location"""
        if location in self.locations:
            x, y, yaw = self.locations[location]
            self.speak(f"Navigating to {location}")
            
            # This would integrate with the navigation module
            # For now, just log the command
            self.logger.info(f"Navigation command: {location} -> ({x}, {y}, {yaw})")
        else:
            self.speak(f"Unknown location: {location}")
            
    def _execute_exploration(self) -> None:
        """Execute exploration mode"""
        self.speak("Starting exploration mode")
        self.logger.info("Exploration mode activated")
        
    def _execute_object_detection(self) -> None:
        """Execute object detection query"""
        self.speak("Scanning for objects")
        self.logger.info("Object detection query")
        
    def _execute_follow_me(self) -> None:
        """Execute follow me mode"""
        self.speak("Starting follow me mode")
        self.logger.info("Follow me mode activated")
        
    def _execute_emergency_stop(self) -> None:
        """Execute emergency stop"""
        if 'Node' in globals() and self.cmd_vel_pub:
            twist = Twist()
            twist.linear.x = 0.0
            twist.angular.z = 0.0
            self.cmd_vel_pub.publish(twist)
            
        self.speak("Emergency stop activated")
        self.logger.warning("Emergency stop executed")
        
    def speak(self, text: str) -> None:
        """Convert text to speech"""
        if not TTS_AVAILABLE:
            self.logger.info(f"TTS: {text}")
            return
            
        try:
            # Create temporary audio file
            tts = gtts.gTTS(text=text, lang='en')
            temp_file = Path("/tmp/voice_output.mp3")
            tts.save(str(temp_file))
            
            # Play audio
            playsound(str(temp_file))
            
            # Clean up
            temp_file.unlink()
            
        except Exception as e:
            self.logger.error(f"Error in text-to-speech: {e}")
            self.logger.info(f"TTS: {text}")  # Fallback to text
            
    def add_location(self, name: str, x: float, y: float, yaw: float) -> None:
        """Add a new navigation location"""
        self.locations[name] = (x, y, yaw)
        self.logger.info(f"Added location: {name} -> ({x}, {y}, {yaw})")
        
    def get_locations(self) -> Dict[str, tuple]:
        """Get all navigation locations"""
        return self.locations.copy()
        
    def is_listening_active(self) -> bool:
        """Check if voice control is actively listening"""
        return self.is_listening
        
    def run(self) -> None:
        """Run voice control (blocking)"""
        self.start_voice_control()
        try:
            while rclpy.ok():
                if 'Node' in globals():
                    rclpy.spin_once(self, timeout_sec=1.0)
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        finally:
            self.stop_voice_control()
            
    def shutdown(self) -> None:
        """Shutdown voice control module"""
        self.logger.info("Shutting down voice control")
        self.stop_voice_control()
        
        if 'Node' in globals():
            self.destroy_node()
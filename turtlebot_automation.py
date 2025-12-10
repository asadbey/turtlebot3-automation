#!/usr/bin/env python3
"""
TurtleBot3 Comprehensive Automation Script
Integrates setup, maintenance, navigation, object detection, and voice control
for both simulation and hardware deployment
"""

import rclpy
import argparse
import logging
import sys
import signal
from pathlib import Path
from typing import Dict, Optional

# Import automation modules
from modules.setup_automation import SetupAutomation
from modules.maintenance_automation import MaintenanceAutomation  
from modules.navigation_automation import NavigationAutomation
from modules.object_detection import ObjectDetection
from modules.voice_control import VoiceControl


class TurtleBotAutomation:
    """Main automation orchestrator for TurtleBot3"""
    
    def __init__(self, config_file: Optional[str] = None, simulation_mode: bool = True):
        """
        Initialize TurtleBot3 automation system
        
        Args:
            config_file: Path to configuration file
            simulation_mode: True for simulation, False for hardware
        """
        self.logger = self._setup_logging()
        self.simulation_mode = simulation_mode
        self.config = self._load_config(config_file)
        self.modules: Dict[str, object] = {}
        self.ros_context = None
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _setup_logging(self) -> logging.Logger:
        """Configure logging system"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('turtlebot_automation.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        return logging.getLogger(__name__)
        
    def _load_config(self, config_file: Optional[str]) -> dict:
        """Load configuration from file or use defaults"""
        default_config = {
            'simulation': {
                'world_name': 'turtlebot3_world',
                'robot_model': 'waffle',
                'headless': False,
                'use_rviz': True
            },
            'navigation': {
                'map_file': None,
                'use_slam': True,
                'localization': False
            },
            'detection': {
                'model_path': 'yolov8n.pt',
                'confidence': 0.5,
                'camera_topic': '/camera/image_raw'
            },
            'voice': {
                'recognition_engine': 'google',
                'tts_engine': 'gtts',
                'wake_word': 'turtlebot'
            },
            'maintenance': {
                'health_check_interval': 30.0,
                'battery_threshold': 20.0,
                'log_level': 'INFO'
            }
        }
        
        if config_file and Path(config_file).exists():
            # TODO: Implement YAML config loading
            self.logger.info(f"Loading config from {config_file}")
        else:
            self.logger.info("Using default configuration")
            
        return default_config
        
    def initialize_ros(self) -> bool:
        """Initialize ROS2 context and nodes"""
        try:
            if not rclpy.ok():
                rclpy.init()
                self.ros_context = rclpy.Context()
                rclpy.init(context=self.ros_context)
                
            self.logger.info("ROS2 initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize ROS2: {e}")
            return False
            
    def initialize_modules(self) -> bool:
        """Initialize all automation modules"""
        try:
            self.logger.info("Initializing automation modules...")
            
            # Initialize modules based on configuration
            self.modules['setup'] = SetupAutomation(self.config, self.simulation_mode)
            self.modules['maintenance'] = MaintenanceAutomation(self.config)
            self.modules['navigation'] = NavigationAutomation(self.config, self.simulation_mode)
            self.modules['detection'] = ObjectDetection(self.config)
            self.modules['voice'] = VoiceControl(self.config)
            
            # Initialize each module
            for name, module in self.modules.items():
                if hasattr(module, 'initialize'):
                    success = module.initialize()
                    if not success:
                        self.logger.error(f"Failed to initialize {name} module")
                        return False
                    self.logger.info(f"{name.capitalize()} module initialized")
                    
            self.logger.info("All modules initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize modules: {e}")
            return False
            
    def run_full_automation(self) -> None:
        """Execute complete automation pipeline"""
        if not self.initialize_ros():
            return
            
        if not self.initialize_modules():
            return
            
        try:
            self.logger.info("Starting full automation pipeline...")
            
            # Run setup if needed
            if self.modules['setup'].needs_setup():
                self.logger.info("Running setup automation...")
                self.modules['setup'].run_setup()
                
            # Start maintenance monitoring
            self.modules['maintenance'].start_monitoring()
            
            # Start navigation system
            self.modules['navigation'].start_navigation()
            
            # Start object detection
            self.modules['detection'].start_detection()
            
            # Start voice control
            self.modules['voice'].start_voice_control()
            
            # Keep the system running
            self.logger.info("Full automation system is running...")
            self._run_main_loop()
            
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        except Exception as e:
            self.logger.error(f"Error in main automation loop: {e}")
        finally:
            self.shutdown()
            
    def run_individual_module(self, module_name: str) -> None:
        """Run specific automation module"""
        if not self.initialize_ros():
            return
            
        if module_name not in self.modules:
            self.logger.error(f"Unknown module: {module_name}")
            return
            
        try:
            self.logger.info(f"Running {module_name} module...")
            module = self.modules[module_name]
            
            if hasattr(module, 'run'):
                module.run()
            elif hasattr(module, 'start_monitoring'):
                module.start_monitoring()
            elif hasattr(module, 'start_navigation'):
                module.start_navigation()
            elif hasattr(module, 'start_detection'):
                module.start_detection()
            elif hasattr(module, 'start_voice_control'):
                module.start_voice_control()
            else:
                self.logger.error(f"Module {module_name} has no run method")
                
        except Exception as e:
            self.logger.error(f"Error running {module_name}: {e}")
        finally:
            self.shutdown()
            
    def _run_main_loop(self) -> None:
        """Main execution loop"""
        try:
            while rclpy.ok():
                # Process ROS callbacks
                rclpy.spin_once(timeout_sec=0.1)
                
                # Check system health
                if not self.modules['maintenance'].is_healthy():
                    self.logger.warning("System health check failed")
                    
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}")
            
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.shutdown()
        sys.exit(0)
        
    def shutdown(self) -> None:
        """Graceful shutdown of all systems"""
        self.logger.info("Shutting down TurtleBot3 automation...")
        
        # Shutdown all modules
        for name, module in self.modules.items():
            try:
                if hasattr(module, 'shutdown'):
                    module.shutdown()
                    self.logger.info(f"{name.capitalize()} module shutdown")
            except Exception as e:
                self.logger.error(f"Error shutting down {name}: {e}")
                
        # Shutdown ROS2
        if rclpy.ok():
            rclpy.shutdown()
            
        self.logger.info("TurtleBot3 automation shutdown complete")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='TurtleBot3 Comprehensive Automation System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full automation in simulation mode
  python turtlebot_automation.py
  
  # Run full automation with hardware
  python turtlebot_automation.py --no-simulation
  
  # Run specific module
  python turtlebot_automation.py --module navigation
  
  # Use custom configuration
  python turtlebot_automation.py --config my_config.yaml
        """
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        help='Configuration file path'
    )
    
    parser.add_argument(
        '--module', '-m',
        type=str,
        choices=['setup', 'maintenance', 'navigation', 'detection', 'voice'],
        help='Run specific module only'
    )
    
    parser.add_argument(
        '--no-simulation',
        action='store_true',
        help='Use hardware instead of simulation'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        
    # Create automation instance
    automation = TurtleBotAutomation(
        config_file=args.config,
        simulation_mode=not args.no_simulation
    )
    
    # Run automation
    if args.module:
        automation.run_individual_module(args.module)
    else:
        automation.run_full_automation()


if __name__ == '__main__':
    main()
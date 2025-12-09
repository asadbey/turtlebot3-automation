#!/usr/bin/env python3
"""
Object Detection Module for TurtleBot3
Handles YOLOv8 object detection with OpenCV and ROS2 integration
Supports both simulation and hardware deployment
"""

import rclpy
import time
import threading
import logging
import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# ROS2 imports
try:
    from rclpy.node import Node
    from sensor_msgs.msg import Image, CameraInfo
    from vision_msgs.msg import Detection2D, Detection2DArray, ObjectHypothesisWithPose
    from std_msgs.msg import Header
    from cv_bridge import CvBridge
except ImportError:
    # Fallback for systems without ROS2 installed
    Node = object
    Image = object
    CameraInfo = object
    Detection2D = object
    Detection2DArray = object
    ObjectHypothesisWithPose = object
    Header = object
    CvBridge = object

# YOLOv8 imports
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    YOLO = None


class ObjectDetection(Node if 'Node' in globals() else object):
    """Handles object detection using YOLOv8 and OpenCV"""
    
    def __init__(self, config: Dict):
        """
        Initialize object detection
        
        Args:
            config: Configuration dictionary
        """
        # Initialize ROS node if available
        if 'Node' in globals():
            super().__init__('object_detection')
            
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Detection configuration
        detection_config = config.get('detection', {})
        self.model_path = detection_config.get('model_path', 'yolov8n.pt')
        self.confidence = detection_config.get('confidence', 0.5)
        self.camera_topic = detection_config.get('camera_topic', '/camera/image_raw')
        
        # State tracking
        self.is_detecting = False
        self.detection_active = False
        self.model = None
        self.bridge = None
        self.class_names = []
        
        # ROS2 subscribers and publishers
        self.image_sub = None
        self.detection_pub = None
        self.image_pub = None
        
        # Detection thread
        self.detection_thread = None
        
        # Performance tracking
        self.detection_count = 0
        self.fps_counter = 0
        self.last_fps_time = time.time()
        
    def initialize(self) -> bool:
        """Initialize object detection module"""
        try:
            self.logger.info("Initializing object detection module")
            
            # Check YOLO availability
            if not YOLO_AVAILABLE:
                self.logger.error("YOLOv8 not available. Install with: pip install ultralytics")
                return False
                
            # Load YOLO model
            if not self._load_model():
                return False
                
            # Setup ROS connections if available
            if 'Node' in globals():
                self._setup_ros_connections()
                self.bridge = CvBridge()
            else:
                self.logger.warning("ROS2 not available, running in simulation mode")
                
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize object detection: {e}")
            return False
            
    def _load_model(self) -> bool:
        """Load YOLOv8 model"""
        try:
            self.logger.info(f"Loading YOLOv8 model: {self.model_path}")
            
            # Check if model file exists
            if not Path(self.model_path).exists():
                self.logger.warning(f"Model file {self.model_path} not found, will download")
                
            # Load model
            self.model = YOLO(self.model_path)
            
            # Get class names
            self.class_names = self.model.names
            
            self.logger.info(f"YOLOv8 model loaded successfully with {len(self.class_names)} classes")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load YOLOv8 model: {e}")
            return False
            
    def _setup_ros_connections(self) -> None:
        """Setup ROS2 subscribers and publishers"""
        try:
            # Image subscriber
            self.image_sub = self.create_subscription(
                Image,
                self.camera_topic,
                self._image_callback,
                10
            )
            
            # Detection publisher
            self.detection_pub = self.create_publisher(
                Detection2DArray,
                '/object_detections',
                10
            )
            
            # Annotated image publisher
            self.image_pub = self.create_publisher(
                Image,
                '/detection_image',
                10
            )
            
            self.logger.info("ROS2 detection connections established")
            
        except Exception as e:
            self.logger.error(f"Failed to setup ROS detection connections: {e}")
            
    def start_detection(self) -> None:
        """Start object detection"""
        if self.detection_active:
            self.logger.warning("Object detection already active")
            return
            
        self.detection_active = True
        self.logger.info("Object detection started")
        
        # Start detection thread
        self.detection_thread = threading.Thread(target=self._detection_loop, daemon=True)
        self.detection_thread.start()
        
    def stop_detection(self) -> None:
        """Stop object detection"""
        self.detection_active = False
        self.is_detecting = False
        
        if self.detection_thread:
            self.detection_thread.join(timeout=5.0)
            
        self.logger.info("Object detection stopped")
        
    def _detection_loop(self) -> None:
        """Main detection loop"""
        while self.detection_active:
            try:
                if 'Node' in globals():
                    rclpy.spin_once(self, timeout_sec=0.1)
                time.sleep(0.01)  # 100 FPS max
            except Exception as e:
                self.logger.error(f"Error in detection loop: {e}")
                time.sleep(0.1)
                
    def _image_callback(self, msg: Image) -> None:
        """Handle incoming camera images"""
        if not self.detection_active or self.is_detecting:
            return
            
        self.is_detecting = True
        
        try:
            # Convert ROS image to OpenCV format
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            
            # Perform object detection
            detections = self._detect_objects(cv_image)
            
            # Publish results
            if self.detection_pub:
                self._publish_detections(detections, msg.header)
                
            # Publish annotated image
            if self.image_pub:
                annotated_image = self._draw_detections(cv_image, detections)
                self._publish_annotated_image(annotated_image, msg.header)
                
            # Update performance metrics
            self._update_performance_metrics()
            
        except Exception as e:
            self.logger.error(f"Error processing image: {e}")
        finally:
            self.is_detecting = False
            
    def _detect_objects(self, image: np.ndarray) -> List[Dict]:
        """
        Perform object detection on image
        
        Args:
            image: OpenCV image
            
        Returns:
            List of detection dictionaries
        """
        try:
            # Run YOLOv8 inference
            results = self.model(image, conf=self.confidence, verbose=False)
            
            detections = []
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Extract bounding box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        confidence = box.conf[0].cpu().numpy()
                        class_id = int(box.cls[0].cpu().numpy())
                        
                        # Create detection dictionary
                        detection = {
                            'bbox': [float(x1), float(y1), float(x2), float(y2)],
                            'confidence': float(confidence),
                            'class_id': class_id,
                            'class_name': self.class_names[class_id] if class_id < len(self.class_names) else 'unknown'
                        }
                        detections.append(detection)
                        
            return detections
            
        except Exception as e:
            self.logger.error(f"Error in object detection: {e}")
            return []
            
    def _draw_detections(self, image: np.ndarray, detections: List[Dict]) -> np.ndarray:
        """
        Draw detection bounding boxes on image
        
        Args:
            image: OpenCV image
            detections: List of detection dictionaries
            
        Returns:
            Annotated image
        """
        annotated_image = image.copy()
        
        for detection in detections:
            bbox = detection['bbox']
            confidence = detection['confidence']
            class_name = detection['class_name']
            
            x1, y1, x2, y2 = map(int, bbox)
            
            # Draw bounding box
            cv2.rectangle(annotated_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw label
            label = f"{class_name}: {confidence:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            
            # Draw label background
            cv2.rectangle(
                annotated_image,
                (x1, y1 - label_size[1] - 10),
                (x1 + label_size[0], y1),
                (0, 255, 0),
                -1
            )
            
            # Draw label text
            cv2.putText(
                annotated_image,
                label,
                (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 0),
                2
            )
            
        # Draw FPS counter
        fps = self._calculate_fps()
        cv2.putText(
            annotated_image,
            f"FPS: {fps:.1f}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )
        
        return annotated_image
        
    def _publish_detections(self, detections: List[Dict], header: Header) -> None:
        """Publish detection results to ROS2 topic"""
        try:
            detection_array = Detection2DArray()
            detection_array.header = header
            
            for detection in detections:
                detection_msg = Detection2D()
                detection_msg.header = header
                
                # Set bounding box (center and size)
                bbox = detection['bbox']
                x1, y1, x2, y2 = bbox
                center_x = (x1 + x2) / 2.0
                center_y = (y1 + y2) / 2.0
                size_x = x2 - x1
                size_y = y2 - y1
                
                # Create detection hypothesis
                hypothesis = ObjectHypothesisWithPose()
                hypothesis.id = detection['class_id']
                hypothesis.score = detection['confidence']
                
                detection_msg.results.append(hypothesis)
                
                # Set bounding box (simplified - in real implementation would use proper ROI)
                detection_msg.bbox.center.x = center_x
                detection_msg.bbox.center.y = center_y
                detection_msg.bbox.size_x = size_x
                detection_msg.bbox.size_y = size_y
                
                detection_array.detections.append(detection_msg)
                
            self.detection_pub.publish(detection_array)
            
        except Exception as e:
            self.logger.error(f"Error publishing detections: {e}")
            
    def _publish_annotated_image(self, image: np.ndarray, header: Header) -> None:
        """Publish annotated image to ROS2 topic"""
        try:
            ros_image = self.bridge.cv2_to_imgmsg(image, encoding='bgr8')
            ros_image.header = header
            self.image_pub.publish(ros_image)
        except Exception as e:
            self.logger.error(f"Error publishing annotated image: {e}")
            
    def _update_performance_metrics(self) -> None:
        """Update performance metrics"""
        self.detection_count += 1
        self.fps_counter += 1
        
    def _calculate_fps(self) -> float:
        """Calculate current FPS"""
        current_time = time.time()
        time_diff = current_time - self.last_fps_time
        
        if time_diff >= 1.0:
            fps = self.fps_counter / time_diff
            self.fps_counter = 0
            self.last_fps_time = current_time
            return fps
        else:
            return self.fps_counter / max(time_diff, 0.001)
            
    def detect_objects_sync(self, image_path: str) -> List[Dict]:
        """
        Synchronous object detection for testing
        
        Args:
            image_path: Path to image file
            
        Returns:
            List of detection dictionaries
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                self.logger.error(f"Could not load image: {image_path}")
                return []
                
            return self._detect_objects(image)
            
        except Exception as e:
            self.logger.error(f"Error in synchronous detection: {e}")
            return []
            
    def get_detection_stats(self) -> Dict:
        """Get detection performance statistics"""
        return {
            'total_detections': self.detection_count,
            'current_fps': self._calculate_fps(),
            'model_path': self.model_path,
            'confidence_threshold': self.confidence,
            'num_classes': len(self.class_names),
            'is_active': self.detection_active
        }
        
    def run(self) -> None:
        """Run object detection (blocking)"""
        self.start_detection()
        try:
            while rclpy.ok():
                rclpy.spin_once(self, timeout_sec=1.0)
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        finally:
            self.stop_detection()
            
    def shutdown(self) -> None:
        """Shutdown object detection module"""
        self.logger.info("Shutting down object detection")
        self.stop_detection()
        
        if 'Node' in globals():
            self.destroy_node()
#!/usr/bin/env python3
"""
Full Automation Launch File for TurtleBot3
Launches complete automation system with simulation, navigation, detection, and voice control
"""

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    """Generate launch description for full automation system"""
    
    # Declare launch arguments
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation time'
    )
    
    headless_arg = DeclareLaunchArgument(
        'headless',
        default_value='false',
        description='Run Gazebo in headless mode'
    )
    
    use_rviz_arg = DeclareLaunchArgument(
        'use_rviz',
        default_value='true',
        description='Launch RViz for visualization'
    )
    
    world_name_arg = DeclareLaunchArgument(
        'world_name',
        default_value='turtlebot3_world',
        description='Gazebo world name'
    )
    
    robot_model_arg = DeclareLaunchArgument(
        'robot_model',
        default_value='waffle',
        description='TurtleBot3 model (burger, waffle, waffle_pi)'
    )
    
    # Set environment variables
    os.environ['TURTLEBOT3_MODEL'] = LaunchConfiguration('robot_model').perform(None)
    
    # Find package directories
    pkg_gazebo_ros = FindPackageShare('gazebo_ros')
    pkg_turtlebot3_gazebo = FindPackageShare('turtlebot3_gazebo')
    pkg_turtlebot3_navigation2 = FindPackageShare('turtlebot3_navigation2')
    pkg_turtlebot3_simulations = FindPackageShare('turtlebot3_simulations')
    
    # Gazebo launch
    gazebo_launch = IncludeLaunchDescription(
        PathJoinSubstitution([
            pkg_turtlebot3_gazebo,
            'launch',
            'turtlebot3_world.launch.py'
        ]),
        launch_arguments={
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'headless': LaunchConfiguration('headless'),
            'world_name': LaunchConfiguration('world_name'),
            'x': '0.0',
            'y': '0.0',
            'z': '0.0'
        }.items()
    )
    
    # Navigation launch
    navigation_launch = IncludeLaunchDescription(
        PathJoinSubstitution([
            pkg_turtlebot3_navigation2,
            'launch',
            'navigation2.launch.py'
        ]),
        launch_arguments={
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'map': '',
            'params_file': PathJoinSubstitution([
                FindPackageShare('turtlebot_automation'),
                'config',
                'nav2_params.yaml'
            ])
        }.items()
    )
    
    # RViz launch
    rviz_launch = IncludeLaunchDescription(
        PathJoinSubstitution([
            pkg_turtlebot3_navigation2,
            'launch',
            'rviz2.launch.py'
        ]),
        condition=IfCondition(LaunchConfiguration('use_rviz')),
        launch_arguments={
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'rviz_config': PathJoinSubstitution([
                FindPackageShare('turtlebot_automation'),
                'config',
                'turtlebot3_view.rviz'
            ])
        }.items()
    )
    
    # Camera bridge for Gazebo
    camera_bridge = Node(
        package='ros_gz_image',
        executable='image_bridge',
        name='camera_bridge',
        output='screen',
        arguments=['/camera/image_raw'],
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}]
    )
    
    # Main automation node
    automation_node = Node(
        package='turtlebot_automation',
        executable='turtlebot_automation',
        name='turtlebot_automation',
        output='screen',
        parameters=[
            {'use_sim_time': LaunchConfiguration('use_sim_time')},
            {'simulation_mode': True},
            {'config_file': PathJoinSubstitution([
                FindPackageShare('turtlebot_automation'),
                'config',
                'automation_config.yaml'
            ])}
        ]
    )
    
    # Object detection node (standalone for testing)
    detection_node = Node(
        package='turtlebot_automation',
        executable='object_detection_node',
        name='object_detection',
        output='screen',
        parameters=[
            {'use_sim_time': LaunchConfiguration('use_sim_time')},
            {'model_path': 'yolov8n.pt'},
            {'confidence': 0.5},
            {'camera_topic': '/camera/image_raw'}
        ]
    )
    
    # Voice control node (standalone for testing)
    voice_node = Node(
        package='turtlebot_automation',
        executable='voice_control_node',
        name='voice_control',
        output='screen',
        parameters=[
            {'use_sim_time': LaunchConfiguration('use_sim_time')},
            {'recognition_engine': 'google'},
            {'tts_engine': 'gtts'},
            {'wake_word': 'turtlebot'}
        ]
    )
    
    # Maintenance monitoring node
    maintenance_node = Node(
        package='turtlebot_automation',
        executable='maintenance_node',
        name='maintenance_automation',
        output='screen',
        parameters=[
            {'use_sim_time': LaunchConfiguration('use_sim_time')},
            {'health_check_interval': 30.0},
            {'battery_threshold': 20.0}
        ]
    )
    
    return LaunchDescription([
        use_sim_time_arg,
        headless_arg,
        use_rviz_arg,
        world_name_arg,
        robot_model_arg,
        gazebo_launch,
        navigation_launch,
        rviz_launch,
        camera_bridge,
        automation_node,
        detection_node,
        voice_node,
        maintenance_node
    ])
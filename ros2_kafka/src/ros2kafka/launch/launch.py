#!/usr/bin/env python3

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    
    config_arg = DeclareLaunchArgument(
        'config_file',
        default_value=PathJoinSubstitution(
            [FindPackageShare('ros2kafka'), 'launch', 'config.yaml']
        ),
        description='Pfad zur Konfigurationsdatei (config.yaml)'
    )
    
    
    # Hole den Wert des Launch-Arguments
    config_file = LaunchConfiguration('config_file')
    
    # Node für kafka_unitree_data_provider
    kafka_unitree_node = Node(
        package='ros2kafka',
        executable='kafka_unitree_data_provider',
        name='kafka_unitree_data_provider',
        output='screen',
        parameters=[config_file]
    )

    # Node für kafka_pointcloud_provider
    kafka_pointcloud_node = Node(
        package='ros2kafka',
        executable='kafka_pointcloud_provider',
        name='kafka_pointcloud_provider',
        output='screen',
        parameters=[config_file]
    )

    # Node für kafka_dynamixel_provider
    kafka_head_node = Node(
        package='ros2kafka',
        executable='kafka_dynamixel_provider',
        name='kafka_head_provider',
        exec_name='kafka_head_provider',
        output='screen',
        parameters=[config_file]
    )
    
    # Node für kafka_dynamixel_provider
    kafka_left_wrist_node = Node(
        package='ros2kafka',
        executable='kafka_dynamixel_provider',
        name='kafka_left_wrist_provider',
        exec_name='kafka_left_wrist_provider',
        output='screen',
        parameters=[config_file]
    )
    
    # Node für kafka_dynamixel_provider
    kafka_right_wrist_node = Node(
        package='ros2kafka',
        executable='kafka_dynamixel_provider',
        name='kafka_right_wrist_provider',
        exec_name='kafka_right_wrist_provider',
        output='screen',
        parameters=[config_file]
    )

    return LaunchDescription([
        config_arg,
        kafka_unitree_node,
        kafka_pointcloud_node,
        kafka_head_node,
        kafka_left_wrist_node,
        kafka_right_wrist_node
    ])

if __name__ == '__main__':
    generate_launch_description()

# -*- coding: utf-8 -*-

import rclpy
from rclpy.node import Node
from rclpy.clock import Clock

from typing import Any

from ros2kafka import KafkaAvroProducer

class RosListenerNode(Node):

    def __init__(self, name:str, ros_type:Any):
        super().__init__(name)
        self.msg_count = 0
        
        # Parameter
        self.declare_parameter('ros_topic', 'my_pose_topic')
        self.ros_topic = self.get_parameter('ros_topic').get_parameter_value().string_value
          
        # Parameter
        self.declare_parameter('is_silent', False)
        self.is_silent = self.get_parameter('is_silent').get_parameter_value().bool_value           
      
        self.get_logger().info(f'Subscribing to topic: {self.ros_topic}')        
        self.subscription = self.create_subscription(
            ros_type,
            self.ros_topic,
            self.on_ros_message,
            10)
        self.subscription  # prevent unused variable warning

    def process_message(self, msg):        
        return None
    
    def send_message(self, msg):        
        pass

    def on_ros_message(self, msg):
        self.msg_count += 1
        self.get_logger().info(f'on_ros_message: {self.msg_count}') 
        processed_msg = self.process_message(msg)
        if (self.is_silent == False and processed_msg):
            self.send_message(processed_msg)

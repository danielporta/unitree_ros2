# -*- coding: utf-8 -*-

import rclpy
from rclpy.node import Node
from rclpy.clock import Clock

from typing import Any

from ros2kafka import KafkaAvroProducer

class KafkaRosNode(Node):

    def __init__(self, name:str, ros_type:Any, key_schema:str, value_schema:str):
        super().__init__(name)
        self.msg_count = 0
        
        # Parameter
        self.declare_parameter('ros_topic', 'my_pose_topic')
        self.ros_topic = self.get_parameter('ros_topic').get_parameter_value().string_value
                
        # Parameter
        self.declare_parameter('kafka_broker', 'localhost:9092')
        self.kafka_broker = self.get_parameter('kafka_broker').get_parameter_value().string_value
                     
        # Parameter
        self.declare_parameter('schema_registry', 'http://localhost:8081')
        self.schema_registry = self.get_parameter('schema_registry').get_parameter_value().string_value
                
        # Parameter
        self.declare_parameter('kafka_topic', 'pose_topic_avro')
        self.kafka_topic = self.get_parameter('kafka_topic').get_parameter_value().string_value        
           
        # Parameter
        self.declare_parameter('is_silent', False)
        self.is_silent = self.get_parameter('is_silent').get_parameter_value().bool_value           
                     
        self.kafka_producer = KafkaAvroProducer(self.kafka_broker, self.schema_registry, self.kafka_topic, key_schema, value_schema)
        self.get_logger().info(f'Connected to Kafka broker at {self.kafka_broker}, topic: {self.kafka_topic}')

        self.get_logger().info(f'Subscribing to topic: {self.ros_topic}')        
        self.subscription = self.create_subscription(
            ros_type,
            self.ros_topic,
            self.on_ros_message,
            10)
        self.subscription  # prevent unused variable warning

    def process_message(self, msg):        
        return (None, None)

    def on_ros_message(self, msg):
        self.msg_count += 1
        self.get_logger().info(f'on_ros_message: {self.msg_count}') 
        processed_msg = self.process_message(msg)
        if (self.is_silent == False):
            self.kafka_producer.produce(processed_msg[0], processed_msg[1])

# -*- coding: utf-8 -*-

import rclpy
from rclpy.node import Node
from rclpy.clock import Clock

from typing import Any

from ros2kafka import KafkaAvroProducer
from ros2kafka import RosListenerNode

class KafkaRosNode(RosListenerNode):

    def __init__(self, name:str, ros_type:Any, key_schema:str, value_schema:str):
        super().__init__(name, ros_type)
        self.msg_count = 0
                      
        # Parameter
        self.declare_parameter('kafka_broker', 'localhost:9092')
        self.kafka_broker = self.get_parameter('kafka_broker').get_parameter_value().string_value
                     
        # Parameter
        self.declare_parameter('schema_registry', 'http://localhost:8081')
        self.schema_registry = self.get_parameter('schema_registry').get_parameter_value().string_value
                
        # Parameter
        self.declare_parameter('kafka_topic', 'pose_topic_avro')
        self.kafka_topic = self.get_parameter('kafka_topic').get_parameter_value().string_value             
                     
        self.kafka_producer = KafkaAvroProducer(self.kafka_broker, self.schema_registry, self.kafka_topic, key_schema, value_schema)
        self.get_logger().info(f'Connected to Kafka broker at {self.kafka_broker}, topic: {self.kafka_topic}')

    def process_message(self, msg):        
        return (None, None)

    def send_message(self, msg):        
        self.kafka_producer.produce(msg[0], msg[1])
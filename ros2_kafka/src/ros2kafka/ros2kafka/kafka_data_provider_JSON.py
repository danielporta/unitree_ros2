# Copyright 2016 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped

from confluent_kafka import Producer
import json

class KafkaDataProviderJSON(Node):

    def __init__(self):
        super().__init__('kafka_data_provider_JSON')
        
        # Parameter
        self.declare_parameter('ros_topic', 'pose_topic')
        self.ros_topic = self.get_parameter('ros_topic').get_parameter_value().string_value
                
        # Parameter
        self.declare_parameter('kafka_broker', 'localhost:9092')
        self.kafka_broker = self.get_parameter('kafka_broker').get_parameter_value().string_value
                
        # Parameter
        self.declare_parameter('kafka_topic', 'pose_topic_json')
        self.kafka_topic = self.get_parameter('kafka_topic').get_parameter_value().string_value
        
        self.kafka_producer = Producer({'bootstrap.servers': self.kafka_broker })
        self.get_logger().info(f'Connected to Kafka broker at {self.kafka_broker}, topic: {self.kafka_topic}')

        self.get_logger().info(f'Subscribing to topic: {self.ros_topic}')        
        self.subscription = self.create_subscription(
            PoseStamped,
            self.ros_topic,
            self.pose_callback,
            10)
        self.subscription  # prevent unused variable warning

    def pose_callback(self, msg):
        self.get_logger().info(f'Received Pose:')
        self.get_logger().info(f' - Frame ID: {msg.header.frame_id}')
        self.get_logger().info(f' - Timestamp: {msg.header.stamp.sec}.{msg.header.stamp.nanosec}')
        self.get_logger().info(f' - Position: x={msg.pose.position.x}, y={msg.pose.position.y}, z={msg.pose.position.z}')
        self.get_logger().info(f' - Orientation: x={msg.pose.orientation.x}, y={msg.pose.orientation.y}, z={msg.pose.orientation.z}, w={msg.pose.orientation.w}')

        pose_data = {
            'header': {
                'frame_id': msg.header.frame_id,
                'stamp': {
                    'sec': msg.header.stamp.sec,
                    'nanosec': msg.header.stamp.nanosec
                }
            },
            'pose': {
                'position': {
                    'x': msg.pose.position.x,
                    'y': msg.pose.position.y,
                    'z': msg.pose.position.z
                },
                'orientation': {
                    'x': msg.pose.orientation.x,
                    'y': msg.pose.orientation.y,
                    'z': msg.pose.orientation.z,
                    'w': msg.pose.orientation.w
                }
            }
        }
        
        try:
            self.kafka_producer.produce(self.kafka_topic, json.dumps(pose_data))
            self.kafka_producer.flush()
            self.get_logger().info(f'Pose sent to Kafka: {pose_data}')
        except Exception as e:
            self.get_logger().error(f'Failed to send pose to Kafka: {e}')

def main(args=None):
    rclpy.init(args=args)

    node = KafkaDataProviderJSON()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

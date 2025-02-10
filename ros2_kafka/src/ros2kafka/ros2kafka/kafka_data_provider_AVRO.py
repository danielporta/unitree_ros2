# -*- coding: utf-8 -*-

import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped

from confluent_kafka import SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import (
    MessageField,
    SerializationContext,
#    StringSerializer,
)

from libavro.de.dfki.cos.mrk40.avro.Pose3dStamped import Pose3dStamped

class KafkaDataProviderAVRO(Node):

    def __init__(self):
        super().__init__('kafka_data_provider_AVRO')
        
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
                
        self.src = SchemaRegistryClient({"url": self.schema_registry})
        self.avro_serializer = AvroSerializer(
            self.src, Pose3dStamped.schema, self.Pose3dStamped_to_dict
        )
        #self.string_serializer = StringSerializer("utf_8")
                
        self.kafka_producer = SerializingProducer({'bootstrap.servers': self.kafka_broker })
        self.get_logger().info(f'Connected to Kafka broker at {self.kafka_broker}, topic: {self.kafka_topic}')

        self.get_logger().info(f'Subscribing to topic: {self.ros_topic}')        
        self.subscription = self.create_subscription(
            PoseStamped,
            self.ros_topic,
            self.pose_callback,
            10)
        self.subscription  # prevent unused variable warning


    def Pose3dStamped_to_dict(self, pose: Pose3dStamped, ctx):
        return pose.dict()
    
    def pose_callback(self, msg):
                     
        pose_data = {
            'pose': {
                'position': {
                    'x': float(msg.pose.position.x),
                    'y': float(msg.pose.position.y),
                    'z': float(msg.pose.position.z)
                },
                'orientation': {
                    'x': float(msg.pose.orientation.x),
                    'y': float(msg.pose.orientation.y),
                    'z': float(msg.pose.orientation.z),
                    'w': float(msg.pose.orientation.w)
                }
            }, 
            'timestamp' : {
                'seconds': msg.header.stamp.sec,
                'nseconds': msg.header.stamp.nanosec
            }
        }
        
        pose = Pose3dStamped(pose_data)          
        
        try:            
            self.kafka_producer.produce(
                topic = self.kafka_topic, 
                # key=string_serializer(str(uuid4())),
                value = self.avro_serializer(pose, SerializationContext(self.kafka_topic, MessageField.VALUE)),
                on_delivery=self.delivery_callback,
            )            
            
            # Trigger any available delivery report callbacks from previous produce() calls
            events_processed = self.kafka_producer.poll(1)
            #print(f"events_processed: {events_processed}")

            messages_in_queue = self.kafka_producer.flush(1)
            #print(f"messages_in_queue: {messages_in_queue}")
            
            
            #self.get_logger().info(f'Pose sent to Kafka: {pose}')
        except Exception as e:
            self.get_logger().error(f'Failed to send pose to Kafka: {e}')    
            self.get_logger().error(f'Data: {pose.dict()}')

    def delivery_callback(self, err, msg):
        if err:
            self.get_logger().error("ERROR: Message failed delivery: {}".format(err))
        else:
            self.get_logger().info(f'Pose sent to Kafka.')
            #self.get_logger().debug(
            #    "Produced event to topic {topic}: key = {key:12} value = {value:12}".format(
            #        topic=msg.topic(),
            #        key="",  # msg.key().decode("utf-8"),
            #        value=msg.value() #.decode("utf-8"),
            #    )
            #)


def main(args=None):
    rclpy.init(args=args)

    node = KafkaDataProviderAVRO()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

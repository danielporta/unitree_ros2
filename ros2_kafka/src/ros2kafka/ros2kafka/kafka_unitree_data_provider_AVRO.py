# -*- coding: utf-8 -*-

import rclpy
from rclpy.node import Node
from rclpy.clock import Clock

from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped
from unitree_go.msg import LowState

from confluent_kafka import SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import (
    MessageField,
    SerializationContext,
#    StringSerializer,
)

from libavro.de.dfki.cos.mrk40.avro.JointStateStamped import JointStateStamped
from libavro.de.dfki.cos.mrk40.avro.SimpleKey import SimpleKey

jointstate_template_dict = {
    'state': {
        'position': [],
        'velocity': [],
        'effort': []
    }, 
    'timestamp' : {
        'seconds': 0,
        'nseconds': 0
    }
}

jointstate = JointStateStamped(jointstate_template_dict)

key_template = {
    'key': 'mykey'
}

key = SimpleKey(key_template)
class KafkaUnitreeDataProviderAVRO(Node):

    def __init__(self):
        super().__init__('kafka_unitree_data_provider_AVRO')
        
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
                
        self.key_serializer = AvroSerializer(
            self.src, SimpleKey.schema, self.key_to_dict
        )
        self.avro_serializer = AvroSerializer(
            self.src, JointStateStamped.schema, self.value_to_dict
        )
                
        self.kafka_producer = SerializingProducer({'bootstrap.servers': self.kafka_broker })
        self.get_logger().info(f'Connected to Kafka broker at {self.kafka_broker}, topic: {self.kafka_topic}')

        self.get_logger().info(f'Subscribing to topic: {self.ros_topic}')        
        self.subscription = self.create_subscription(
            LowState,
            self.ros_topic,
            self.send_callback,
            10)
        self.subscription  # prevent unused variable warning


    def key_to_dict(self, data: SimpleKey, ctx):
        return data.dict()
       
    def value_to_dict(self, data: JointStateStamped, ctx):
        return data.dict()
    
    
    def debug_callback(self, msg):
        self.get_logger().info(f'New State')
        
        stamp = Clock().now().to_msg()   
        jointstate.timestamp.seconds = stamp.sec
        jointstate.timestamp.nseconds = stamp.nanosec    
        jointstate.state.position = []
        for motor_state in msg.motor_state:            
            jointstate.state.position.append(motor_state.q)
                
        self.get_logger().info(f'JointState: {jointstate.dict()}')
        
    def send_callback(self, msg):                     
        stamp = Clock().now().to_msg()   
        jointstate.timestamp.seconds = stamp.sec
        jointstate.timestamp.nseconds = stamp.nanosec    
        jointstate.state.position = []
        for motor_state in msg.motor_state:            
            jointstate.state.position.append(motor_state.q)
        
        try:            
            self.kafka_producer.produce(
                topic = self.kafka_topic, 
                key = self.key_serializer(key, SerializationContext(self.kafka_topic, MessageField.KEY)),
                value = self.avro_serializer(jointstate, SerializationContext(self.kafka_topic, MessageField.VALUE)),
                on_delivery=self.delivery_callback,
            )            
            
            # Trigger any available delivery report callbacks from previous produce() calls
            events_processed = self.kafka_producer.poll(1)
            #print(f"events_processed: {events_processed}")

            messages_in_queue = self.kafka_producer.flush(1)
            #print(f"messages_in_queue: {messages_in_queue}")
            
            
            #self.get_logger().info(f'Pose sent to Kafka: {data}')
        except Exception as e:
            self.get_logger().error(f'Failed to send data to Kafka: {e}')    
            self.get_logger().error(f'Data: {data.dict()}')

    def delivery_callback(self, err, msg):
        if err:
            self.get_logger().error("ERROR: Message failed delivery: {}".format(err))
        #else:
            #self.get_logger().info(f'Data sent to Kafka.')
            #self.get_logger().debug(
            #    "Produced event to topic {topic}: key = {key:12} value = {value:12}".format(
            #        topic=msg.topic(),
            #        key="",  # msg.key().decode("utf-8"),
            #        value=msg.value() #.decode("utf-8"),
            #    )
            #)


def main(args=None):
    rclpy.init(args=args)

    node = KafkaUnitreeDataProviderAVRO()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

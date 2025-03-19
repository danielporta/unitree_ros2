# -*- coding: utf-8 -*-

import rclpy
from rclpy.node import Node
from rclpy.clock import Clock

from typing import Any
from ros2kafka import KafkaRosNode

from std_msgs.msg import Float32MultiArray

from libavro.de.dfki.cos.mrk40.avro.JointStateStamped import JointStateStamped
from libavro.de.dfki.cos.mrk40.avro.SimpleKey import SimpleKey

value_template_dict = {
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

jointstate = JointStateStamped(value_template_dict)

key = SimpleKey({'key': 'mykey'})

class KafkaDynamixelProvider(KafkaRosNode):

    def __init__(self, name:str, ros_type:Any, key_schema:str, value_schema:str):
        super().__init__(name, ros_type, key_schema, value_schema)
        
    def process_message(self, msg):
        stamp = Clock().now().to_msg()   
        jointstate.timestamp.seconds = stamp.sec
        jointstate.timestamp.nseconds = stamp.nanosec    
        jointstate.state.position = msg.data
            
        return (key, jointstate)
    

def main(args=None):
    rclpy.init(args=args)

    node = KafkaDynamixelProvider('kafka_dynamixel_provider', Float32MultiArray, SimpleKey.schema, JointStateStamped.schema)

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

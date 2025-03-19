# -*- coding: utf-8 -*-

import rclpy
from rclpy.node import Node
from rclpy.clock import Clock

from typing import Any
from ros2kafka import KafkaRosNode

from unitree_go.msg import LowState

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

class KafkaUnitreeDataProvider(KafkaRosNode):

    def __init__(self, name:str, ros_type:Any, key_schema:str, value_schema:str):
        super().__init__(name, ros_type, key_schema, value_schema)
        
    def process_message(self, msg):
        stamp = Clock().now().to_msg()   
        jointstate.timestamp.seconds = stamp.sec
        jointstate.timestamp.nseconds = stamp.nanosec    
        jointstate.state.position = []
        for motor_state in msg.motor_state:            
            jointstate.state.position.append(motor_state.q)
            
        return (key, jointstate)
    

def main(args=None):
    rclpy.init(args=args)

    node = KafkaUnitreeDataProvider('kafka_unitree_data_provider', LowState, SimpleKey.schema, JointStateStamped.schema)

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

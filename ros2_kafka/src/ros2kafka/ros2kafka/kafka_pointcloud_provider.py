# -*- coding: utf-8 -*-

import rclpy
from rclpy.node import Node
from rclpy.clock import Clock

from typing import Any
from ros2kafka import KafkaRosNode

from sensor_msgs.msg import PointCloud2

from libavro.de.dfki.cos.mrk40.avro.PointCloudStamped import PointCloudStamped
from libavro.de.dfki.cos.mrk40.avro.PointField import PointField
from libavro.de.dfki.cos.mrk40.avro.SimpleKey import SimpleKey

value_template_dict = {
    'pc': {
        'height': 0,
        'width': 0,
        'fields': [],
        'is_bigendian': False,
        'point_step': 0,
        'row_step': 0,
        'data' : bytes(),
        'is_dense': False
    }, 
    'timestamp' : {
        'seconds': 0,
        'nseconds': 0
    }
}

pointcloud = PointCloudStamped(value_template_dict)

key = SimpleKey({'key': 'mykey'})

class KafkaPointCloudProvider(KafkaRosNode):

    def __init__(self, name:str, ros_type:Any, key_schema:str, value_schema:str):
        super().__init__(name, ros_type, key_schema, value_schema)
        
    def process_message(self, msg):                
        pointcloud.timestamp.seconds = msg.header.stamp.sec
        pointcloud.timestamp.nseconds = msg.header.stamp.nanosec    
        pointcloud.pc.height = msg.height
        pointcloud.pc.width = msg.width
        pointcloud.pc.is_bigendian = msg.is_bigendian
        pointcloud.pc.point_step = msg.point_step
        pointcloud.pc.row_step = msg.row_step
        pointcloud.pc.is_dense = msg.is_dense
        pointcloud.pc.fields = [PointField({'name': f.name, 'offset': f.offset, 'datatype': f.datatype, 'count': f.count}) for f in msg.fields]
        pointcloud.pc.data = bytes(msg.data)
            
        return (key, pointcloud)
    

def main(args=None):
    rclpy.init(args=args)

    node = KafkaPointCloudProvider('kafka_pointcloud_provider', PointCloud2, SimpleKey.schema, PointCloudStamped.schema)

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

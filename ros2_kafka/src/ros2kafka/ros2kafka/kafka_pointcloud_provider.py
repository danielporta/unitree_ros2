# -*- coding: utf-8 -*-

import rclpy
from rclpy.node import Node
from rclpy.clock import Clock

from typing import Any

import socket
import base64
import json
import gzip
import struct

from ros2kafka import RosListenerNode

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

class KafkaPointCloudProvider(RosListenerNode):

    def __init__(self, name:str, ros_type:Any):
        super().__init__(name, ros_type)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
         # Parameter
        self.declare_parameter('pointcloud_server_ip', 'localhost')
        self.pointcloud_server_ip = self.get_parameter('pointcloud_server_ip').get_parameter_value().string_value        
          
         # Parameter
        self.declare_parameter('pointcloud_server_port', 5000)
        self.pointcloud_server_port = self.get_parameter('pointcloud_server_port').get_parameter_value().integer_value         
        
        try:
            server_address = (self.pointcloud_server_ip, self.pointcloud_server_port)
            self.client_socket.connect(server_address)
        except Exception as e:
            self.get_logger().info("Error opening socket connection", e)
    
    def destroy_node(self):
        self.client_socket.close()
        return super().destroy_node()
        
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
        
        #self.get_logger().info(f'uncompressed size: {len(msg.data)}') 
        
        #pointcloud.pc.data = zlib.compress(msg.data, 1)
        
        dct = pointcloud.dict()
        dct['pc']['data'] = base64.b64encode(msg.data).decode('utf-8')
        
        #pointcloud.pc.data = bytes(msg.data)
               
        #self.get_logger().info(f'  compressed size: {len(pointcloud.pc.data)}') 
        
        #self.get_logger().info(f'{dct}') 
        
        # Serialisierung in JSON
        json_data = json.dumps(dct)
        json_bytes = json_data.encode('utf-8')

        # Komprimierung der JSON-Daten mit GZip
        compressed_data = gzip.compress(json_bytes, gzip._COMPRESS_LEVEL_FAST)              
        length_bytes = struct.pack('!I', len(compressed_data))            
       
        return (length_bytes, compressed_data)
       
       
    def send_message(self, msg):    
        try:
            # Zuerst Länge, dann die komprimierten Daten senden
            self.client_socket.sendall(msg[0])            
            self.client_socket.sendall(msg[1])
            self.get_logger().info(f"data compressed and sent: {len(msg[1])} bytes")
        except Exception as e:
            self.get_logger().info("Error sending message", e)    
        

def main(args=None):
    rclpy.init(args=args)

    node = KafkaPointCloudProvider('kafka_pointcloud_provider', PointCloud2)

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-

import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped, Pose

class SamplePosePubliser(Node):

    def __init__(self):
        super().__init__('sample_pose_publisher')
        
        # Parameter
        self.declare_parameter('ros_topic', 'pose_topic')
        ros_topic = self.get_parameter('ros_topic').get_parameter_value().string_value

        # Parameter
        self.declare_parameter('update_rate', 1.0)
        update_rate = self.get_parameter('update_rate').get_parameter_value().double_value

        
        self.publisher_ = self.create_publisher(PoseStamped, ros_topic, 10)        
        self.get_logger().info(f'Publishing to topic: {ros_topic}')
        
        self.timer = self.create_timer(1.0/update_rate, self.publish_pose)
        self.i = 0

    def timer_callback_simple(self):
        msg = String()
        msg.data = 'Hello World: %d' % self.i
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg.data)
        self.i += 1
        
    def publish_pose(self):
        pose_stamped = PoseStamped()
        
        # Setze Header
        pose_stamped.header.stamp = self.get_clock().now().to_msg()
        pose_stamped.header.frame_id = 'map'
        
        # Setze Position
        pose_stamped.pose.position.x = 1.0
        pose_stamped.pose.position.y = 2.0
        pose_stamped.pose.position.z = 0.0
        
        # Setze Orientierung (Quaternion)
        pose_stamped.pose.orientation.x = 0.0
        pose_stamped.pose.orientation.y = 0.0
        pose_stamped.pose.orientation.z = 0.0
        pose_stamped.pose.orientation.w = 1.0
        
        # Publiziere die Nachricht
        self.publisher_.publish(pose_stamped)
        self.get_logger().info(f'Pose published: {pose_stamped}')
        self.i += 1

def main(args=None):
    rclpy.init(args=args)

    sample_pose_publisher = SamplePosePubliser()

    try:
        rclpy.spin(sample_pose_publisher)
    except KeyboardInterrupt:
        pass
    finally:
        sample_pose_publisher.destroy_node()
        rclpy.shutdown()

    rclpy.spin(sample_pose_publisher)

if __name__ == '__main__':
    main()

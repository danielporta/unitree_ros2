#!/bin/bash
echo "Setup unitree ros2 environment with default interface"
source /opt/ros/jazzy/setup.bash
source cyclonedds_ws/install/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

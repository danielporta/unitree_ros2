#!/bin/bash
echo "Setup unitree ros2 environment"
source /opt/ros/jazzy/setup.bash
source cyclonedds_ws/install/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export CYCLONEDDS_URI='<CycloneDDS><Domain><General><Interfaces>
                            <NetworkInterface name="enp4s0" priority="default" multicast="default" />
                        </Interfaces></General></Domain></CycloneDDS>'

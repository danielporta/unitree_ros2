# ROS2Kafka 
This example project illuistrates how to provision data from a ROS2 topic to Apache Kafka

## Building

1. We use a preconfigured devcontainer environment in VS Code on Ubuntu 24. So you have to first install docker and then build the docker image.

```
docker build .devcontainer/
```

2. Then open VS Code and agree to open the folder in 'devcontainer mode' (just click yes when asked).

```
code .
```

3. Create and activate the virtual environment, then install the requirements.

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r ros2_kafka/src/ros2kafka/requirements_kafka.txt
pip install -r ros2_kafka/src/ros2kafka/requirements_simrk.txt -i https://nexus.basys.dfki.dev/repository/pypi-group/simple 
```

4. Build the ROS2 project

```
colcon build
```

5. Unfortunately, I did not figure out how to automatically copy the installed Python requirements to the install folder created by colcon. As long as there is no better solution please do that manually.

```
cp -r .venv/lib/python3.12/site-packages/* install/ros2kafka/lib/python3.12/site-packages
```

## Replaying Unitree Data

Prerequisits: You have a running Apache Kafka installation together with a Schema Registry (only needed for AVRO format). You can then configure endpoints and topics in config.yaml

1. Start the ROS2 node that transforms and provisions data to Apache Kafka in AVRO format in a new terminal.

```
source install/setup.bash 
ros2 run ros2kafka kafka_unitree_data_provider --ros-args --params-file config.yaml
ros2 run ros2kafka kafka_pointcloud_provider --ros-args --params-file config.yaml
ros2 run ros2kafka kafka_head_provider --ros-args --params-file config.yaml
ros2 run ros2kafka kafka_left_wrist_provider --ros-args --params-file config.yaml
ros2 run ros2kafka kafka_right_wrist_provider --ros-args --params-file config.yaml
```

They can also be launched all together.

```
source install/setup.bash 
ros2 launch ros2kafka launch.py
```


2. Replay the rosbag data.

```
source install/setup.bash 
ros2 bag play --loop --topics lowstate --log-level info h1_bag/
ros2 bag play --loop --topics zed_point_cloud --log-level info zed_bag/
ros2 bag play --loop  --log-level info dynamixels_with_pointcloud/
```

## Running Kafka Example

Prerequisits: You have a running Apache Kafka installation together with a Schema Registry (only needed for AVRO format). You can then configure endpoints and topics in config.yaml

1. Start the ROS2 publisher node in a new terminal.

```
source install/setup.bash 
ros2 run ros2kafka sample_pose_publisher --ros-args --params-file config.yaml
```

2. Start the ROS2 node that provisions data to Apache Kafka in JSON format in a new terminal.

```
source install/setup.bash 
ros2 run ros2kafka kafka_data_provider_JSON --ros-args --params-file config.yaml
```

3. Alternatively or additionally, start the ROS2 node that provisions data to Apache Kafka in AVRO format in a new terminal.

```
source install/setup.bash 
ros2 run ros2kafka kafka_data_provider_AVRO --ros-args --params-file config.yaml
```


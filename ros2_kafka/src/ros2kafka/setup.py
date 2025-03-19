from setuptools import find_packages, setup

package_name = 'ros2kafka'

setup(
    name=package_name,
    version='1.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools', 'confluent-kafka', 'fastavro', 'libavro'],
    zip_safe=True,
    maintainer='Daniel Porta',
    maintainer_email='daniel.porta@dfki.de',
    description='Provisioning of ROS2 data to Apache Kafka',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'kafka_unitree_data_provider = ros2kafka.kafka_unitree_data_provider:main',
            'kafka_pointcloud_provider = ros2kafka.kafka_pointcloud_provider:main'
        ],
    },
)

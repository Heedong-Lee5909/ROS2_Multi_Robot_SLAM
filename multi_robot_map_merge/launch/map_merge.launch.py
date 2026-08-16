from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package="multi_robot_map_merge",
            executable="map_merge_node",
            output="screen",
        )
    ]
    )
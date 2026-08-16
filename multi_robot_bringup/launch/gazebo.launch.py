from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.actions import OpaqueFunction
from launch.substitutions import Command
import tempfile
import random

from ament_index_python.packages import get_package_share_directory

import os


# Create a static TF between the global world frame and each robot's map frame.
# Global world frame과 각 robot의 map frame 사이에 static TF를 생성한다.
def static_tf_node(namespace, x, y):
    return Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name=f"{namespace}_world_tf",
        arguments=[
            # Set the position of the robot's map frame in the world frame.
            # world frame에서 robot map frame의 위치를 설정한다.
            str(x), str(y), "0",

            # No rotation between world and map frames.
            # world와 map frame 사이에는 rotation을 적용하지 않는다.
            "0", "0", "0",

            "world",
            f"{namespace}/map",
        ],
    )


# Generate a robot-specific SDF file by modifying the default TurtleBot3 SDF.
# 기본 TurtleBot3 SDF를 robot별 namespace에 맞게 수정하여 새로운 SDF 파일을 생성한다.
def generate_sdf(namespace):
    # Load the original TurtleBot3 model SDF.
    # TurtleBot3의 기본 model SDF 파일을 불러온다.
    with open(
        os.path.join(
            get_package_share_directory("multi_robot_bringup"),
            "models",
            "model.sdf"
        ),
        "r"
    ) as f:
        sdf = f.read()

    # Add the robot namespace to the odometry frame.
    # odometry frame에 robot namespace를 추가한다.
    sdf = sdf.replace(
        "<odometry_frame>odom</odometry_frame>",
        f"<odometry_frame>{namespace}/odom</odometry_frame>"
    )

    # Add the robot namespace to the base footprint frame.
    # base_footprint frame에 robot namespace를 추가한다.
    sdf = sdf.replace(
        "<robot_base_frame>base_footprint</robot_base_frame>",
        f"<robot_base_frame>{namespace}/base_footprint</robot_base_frame>"
    )

    # Add the robot namespace to the LiDAR frame.
    # LiDAR frame인 base_scan에도 robot namespace를 추가한다.
    sdf = sdf.replace(
        "<frame_name>base_scan</frame_name>",
        f"<frame_name>{namespace}/base_scan</frame_name>"
    )

    # Create a temporary SDF file for this robot.
    # 해당 robot을 위한 임시 SDF 파일을 생성한다.
    fd, temp_path = tempfile.mkstemp(suffix=".sdf")

    with os.fdopen(fd, "w") as f:
        f.write(sdf)

    return temp_path


# Create a Gazebo spawn node for a robot.
# Gazebo에서 robot을 spawn하기 위한 Node를 생성한다.
def spawn_robot(name, namespace, x, y):
    return Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        arguments=[
            # Entity name used by Gazebo.
            # Gazebo에서 사용할 robot entity 이름이다.
            "-entity", name,

            # Use the namespace-specific SDF generated above.
            # 위에서 생성한 namespace별 SDF 파일을 사용한다.
            "-file", generate_sdf(namespace),

            # Set the initial robot position.
            # Robot의 초기 spawn 위치를 설정한다.
            "-x", str(x),
            "-y", str(y),
            "-z", "0.01",

            # Assign the ROS namespace to the spawned robot.
            # Spawn된 robot에 ROS namespace를 적용한다.
            "-robot_namespace", namespace
            ],
    )


# Create a Robot State Publisher node for each robot.
# 각 robot에 대한 Robot State Publisher Node를 생성한다.
def robot_state_publisher_node(namespace):

    # Generate the robot description from the TurtleBot3 Burger URDF.
    # TurtleBot3 Burger URDF를 이용하여 robot description을 생성한다.
    robot_description = Command([
        "xacro ",
        os.path.join(
            get_package_share_directory("turtlebot3_description"),
            "urdf",
            "turtlebot3_burger.urdf"
        )
    ])

    return Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",

        # Run the node under the robot-specific namespace.
        # Robot별 namespace에서 Robot State Publisher를 실행한다.
        namespace=namespace,

        parameters=[{
            "robot_description": robot_description,

            # Prefix all TF frames with the robot namespace.
            # 모든 TF frame 앞에 robot namespace를 붙인다.
            "frame_prefix": f"{namespace}/"
            }]
    )


# Spawn multiple robots based on the requested number.
# 설정된 robot 수에 따라 여러 robot을 spawn한다.
def spawn_robots(context):

    # Read the number of robots from the launch argument.
    # Launch argument에서 spawn할 robot의 수를 가져온다.
    num_robots = int(
        LaunchConfiguration("num_robots").perform(context)
    )

    # Candidate positions for robot spawning.
    # Robot을 spawn할 수 있는 후보 위치를 정의한다.
    spawn_candidates = [
        (-4.5, 4.2),
        (4.5, 4.2),
        (-6.0, -3.3),
        #(-1.5, -2.0),
        #(3.8, -3.8)
    ]

    # Randomly select unique spawn positions for the robots.
    # 여러 robot이 동일한 위치에 spawn되지 않도록
    # 후보 위치에서 random으로 서로 다른 위치를 선택한다.
    spawn_positions = random.sample(
        spawn_candidates, num_robots
    )

    actions = []

    # Create the required nodes for each robot.
    # 각 robot에 필요한 Node들을 생성한다.
    for i in range(num_robots):
        x, y = spawn_positions[i]

        # Spawn the TurtleBot3 in Gazebo.
        # Gazebo에 TurtleBot3를 spawn한다.
        actions.append(
            spawn_robot(
                f"burger_{i+1}",
                f"tb3_{i}",
                x,
                y
            )
        )

        # Publish the robot's TF tree.
        # 해당 robot의 TF tree를 publish한다.
        actions.append(
            robot_state_publisher_node(f"tb3_{i}")
        )

        # Connect the robot's map frame to the global world frame.
        # Robot의 map frame과 global world frame을 연결한다.
        actions.append(
            static_tf_node(f"tb3_{i}", x, y)
        )

    return actions


# Generate the complete launch description.
# 전체 launch configuration을 생성한다.
def generate_launch_description():

    # Locate the TurtleBot3 House World file.
    # TurtleBot3 House World 파일의 경로를 가져온다.
    world = os.path.join(
            get_package_share_directory("turtlebot3_gazebo"),
            "worlds",
            "turtlebot3_house.world"
        )

    actions = [
        # Declare the number of robots as a launch argument.
        # Spawn할 robot 수를 launch argument로 정의한다.
        DeclareLaunchArgument(
            "num_robots",
            default_value="3"
        ),

        # Launch Gazebo with the TurtleBot3 House World.
        # TurtleBot3 House World를 이용하여 Gazebo를 실행한다.
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(
                get_package_share_directory("gazebo_ros"),
                "launch",
                "gazebo.launch.py"
                )
            ),

            launch_arguments={
                "world": world
            }.items(),
        )
    ]

    # Dynamically spawn the requested number of robots.
    # 설정된 robot 수에 따라 동적으로 robot들을 spawn한다.
    actions.append(
        OpaqueFunction(function=spawn_robots)
    )

    return LaunchDescription(actions)
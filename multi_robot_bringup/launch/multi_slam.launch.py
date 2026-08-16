from launch import LaunchDescription
from launch_ros.actions import Node


# Create a SLAM Toolbox node for a specific robot namespace.
# 특정 robot namespace에 대한 SLAM Toolbox Node를 생성한다.
def slam_node(namespace):
    return Node(
        package="slam_toolbox",
        executable="async_slam_toolbox_node",

        # Run SLAM Toolbox under the robot-specific namespace.
        # Robot별 namespace에서 SLAM Toolbox를 실행한다.
        namespace=namespace,

        name="slam_toolbox",
        output="screen",

        parameters=[
            {
                # Use Gazebo simulation time instead of system time.
                # 실제 시간 대신 Gazebo simulation time을 사용한다.
                "use_sim_time": True,

                # Specify the LaserScan topic used by this robot.
                # 해당 robot의 LaserScan topic을 지정한다.
                "scan_topic": f"/{namespace}/scan",

                # Specify the robot's odometry frame.
                # 해당 robot의 odometry frame을 지정한다.
                "odom_frame": f"{namespace}/odom",

                # Specify the robot's base footprint frame.
                # 해당 robot의 base footprint frame을 지정한다.
                "base_frame": f"{namespace}/base_footprint",

                # Specify the robot-specific SLAM map frame.
                # 해당 robot의 SLAM map frame을 지정한다.
                "map_frame": f"{namespace}/map",
            }
        ],

        # Remap SLAM Toolbox's default map-related topics
        # to robot-specific map topics.
        # SLAM Toolbox의 기본 map 관련 topic을
        # robot별 topic으로 remapping한다.
        remappings=[
            # Publish the robot's local map under its namespace.
            # Robot의 local map을 robot namespace에 맞는 topic으로 publish한다.
            ("/map", f"/{namespace}/map"),

            # Publish metadata for the robot-specific map.
            # Robot별 map metadata를 publish한다.
            ("/map_metadata", f"/{namespace}/map_metadata"),

            # Publish updates for the robot-specific map.
            # Robot별 map update 정보를 publish한다.
            ("/map_updates", f"/{namespace}/map_updates"),
        ],

    )


# Generate the complete launch description.
# 전체 SLAM launch configuration을 생성한다.
def generate_launch_description():

    # Store the SLAM Toolbox nodes for all robots.
    # 모든 robot의 SLAM Toolbox Node를 저장한다.
    actions = []

    # Create one independent SLAM Toolbox instance for each robot.
    # 각 robot마다 하나의 independent SLAM Toolbox instance를 생성한다.
    for i in range(3):

        # Generate the robot namespace: tb3_0, tb3_1, tb3_2
        # Robot별 namespace를 생성한다.
        namespace = f"tb3_{i}"

        actions.append(
            slam_node(namespace)
        )

    # Return all three SLAM nodes as the launch description.
    # 생성된 3개의 SLAM Node를 하나의 launch description으로 반환한다.
    return LaunchDescription(actions)
import rclpy
from rclpy.node import Node

# Occupancy Grid(Map) Message
# 각 Robot의 SLAM map을 전달받기 위한 OccupancyGrid message
from nav_msgs.msg import OccupancyGrid

# Numerical Array Library
# OccupancyGrid 데이터를 2D array로 처리하기 위한 NumPy
import numpy as np

# Quaternion -> Euler(Yaw) Conversion
# TF의 quaternion rotation을 yaw angle로 변환
from tf_transformations import euler_from_quaternion

# Degree / Radian Conversion
# LiDAR 및 map 좌표 계산에 사용할 수학 함수
import math
import tf2_ros


class MapMergeNode(Node):

    def __init__(self):

        # Initialize ROS2 Node
        # ROS2 Node를 초기화한다.
        super().__init__("map_merge_node")

        # =====================================================
        # Store each robot's OccupancyGrid information
        #
        # 각 Robot의 local map 정보를 dictionary에 저장한다.
        #
        # Example
        # self.maps["tb3_0"] = {
        #     array,
        #     origin,
        #     resolution,
        #     width,
        #     height
        # }
        # =====================================================
        self.maps = {}

        # =====================================================
        # Subscribe each robot's OccupancyGrid
        #
        # 3대 Robot의 local map을 각각 subscribe한다.
        # =====================================================

        self.create_subscription(
            OccupancyGrid,
            "/tb3_0/map",
            self.map0_callback,
            10          # QoS Queue Size
        )

        self.create_subscription(
            OccupancyGrid,
            "/tb3_1/map",
            self.map1_callback,
            10
        )

        self.create_subscription(
            OccupancyGrid,
            "/tb3_2/map",
            self.map2_callback,
            10
        )

        # =====================================================
        # Publisher
        #
        # Publish merged OccupancyGrid
        # 3개의 local map을 merge한 global map을 publish한다.
        # =====================================================
        self.map_pub = self.create_publisher(
            OccupancyGrid,
            "/merged_map",
            10
        )

        # Create TF2 buffer and listener
        # Robot map frame과 world frame 사이의 TF를 조회하기 위해 사용한다.
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(
            self.tf_buffer,
            self
        )

        self.get_logger().info("Map Merge Node Started")


    # =====================================================
    # Map Callback (Robot 0)
    #
    # Receive OccupancyGrid from tb3_0
    # tb3_0의 local OccupancyGrid를 수신한다.
    # =====================================================
    def map0_callback(self, msg):

        # -----------------------------------------------
        # OccupancyGrid.data is a 1D array.
        #
        # OccupancyGrid의 data는 1D array로 전달된다.
        # 이를 map의 width와 height에 맞는 2D NumPy array로 변환한다.
        #
        # Before
        # data =
        # [0 0 0 100 100 ...]
        #
        # After
        # map_array =
        # [[...],
        #  [...],
        #  [...]]
        # -----------------------------------------------
        map_array = np.array(msg.data).reshape(
            msg.info.height,
            msg.info.width
        )

        # -----------------------------------------------
        # Save map information
        #
        # Robot의 local map과 관련된 정보를 저장한다.
        # -----------------------------------------------
        self.maps["tb3_0"] = {
            "array": map_array,
            "resolution": msg.info.resolution,
            "origin_x": msg.info.origin.position.x,
            "origin_y": msg.info.origin.position.y,
            "width": msg.info.width,
            "height": msg.info.height
        }

        # Print received map information
        # 수신한 map의 기본 정보를 출력한다.
        self.get_logger().info(
            f"""
            tb3_0

            width : {msg.info.width}
            height : {msg.info.height}

            resolution : {msg.info.resolution}

            origin :
            ({msg.info.origin.position.x:.2f},
            {msg.info.origin.position.y:.2f})
            """
        )


    # =====================================================
    # Map Callback (Robot 1)
    #
    # Same logic as tb3_0
    # tb3_0과 동일한 방식으로 tb3_1의 map을 저장한다.
    # =====================================================
    def map1_callback(self, msg):

        map_array = np.array(msg.data).reshape(
            msg.info.height,
            msg.info.width
        )

        self.maps["tb3_1"] = {
            "array": map_array,
            "resolution": msg.info.resolution,
            "origin_x": msg.info.origin.position.x,
            "origin_y": msg.info.origin.position.y,
            "width": msg.info.width,
            "height": msg.info.height
        }

        self.get_logger().info(
            f"""
            tb3_1

            width : {msg.info.width}
            height : {msg.info.height}

            resolution : {msg.info.resolution}

            origin :
            ({msg.info.origin.position.x:.2f},
            {msg.info.origin.position.y:.2f})
            """
        )


    # =====================================================
    # Map Callback (Robot 2)
    #
    # Same logic as the previous callbacks.
    # tb3_0, tb3_1과 동일한 방식으로 tb3_2의 map을 저장한다.
    #
    # After receiving the third map,
    # start map merging.
    # 3번째 map까지 수신되면 map merging을 시작한다.
    # =====================================================
    def map2_callback(self, msg):

        map_array = np.array(msg.data).reshape(
            msg.info.height,
            msg.info.width
        )

        self.maps["tb3_2"] = {
            "array": map_array,
            "resolution": msg.info.resolution,
            "origin_x": msg.info.origin.position.x,
            "origin_y": msg.info.origin.position.y,
            "width": msg.info.width,
            "height": msg.info.height
        }

        self.get_logger().info(
            f"""
            tb3_2

            width : {msg.info.width}
            height : {msg.info.height}

            resolution : {msg.info.resolution}

            origin :
            ({msg.info.origin.position.x:.2f},
            {msg.info.origin.position.y:.2f})
            """
        )

        # -----------------------------------------------
        # Start merging only after all three maps
        # have been received at least once.
        #
        # 3개의 local map을 모두 한 번 이상 수신한 경우
        # map merging을 시작한다.
        # -----------------------------------------------
        if len(self.maps) == 3:
            self.merge_maps()


    # =====================================================
    # Get the transform from a robot's map frame to world.
    #
    # 각 Robot의 map frame과 global world frame 사이의
    # 현재 TF transform을 조회한다.
    # =====================================================
    def get_robot_world_transform(self, robot_name):
        try:

            transform = self.tf_buffer.lookup_transform(
                "world",
                f"{robot_name}/map",
                rclpy.time.Time()
            )

            return transform

        except Exception as e:

            # TF가 아직 available하지 않은 경우 merge를 수행하지 않는다.
            self.get_logger().warn(
                f"TF lookup failed: {robot_name} -> world: {e}"
            )

            return None
        

    # =====================================================
    # Merge Local Maps
    #
    # Create one global occupancy grid by combining
    # all local occupancy grids.
    #
    # 각 Robot의 local OccupancyGrid를 world coordinate에
    # 맞춰 하나의 global OccupancyGrid로 merge한다.
    # =====================================================
    def merge_maps(self):

        self.get_logger().info("Start Map Merge")

        # =================================================
        # Step 1. Find Global Bounding Box
        #
        # Calculate the minimum and maximum world
        # coordinates that contain every local map.
        #
        # 모든 local map을 포함할 수 있는
        # global bounding box를 계산한다.
        #
        #           global_max
        #              ●
        #              │
        #      ┌───────┼────────┐
        #      │       │        │
        #      │ Local Maps     │
        #      │                │
        #      └───────┼────────┘
        #              │
        #              ●
        #          global_min
        # =================================================

        # Initialize with infinity
        # 처음에는 최소/최대 좌표를 infinity로 초기화한다.
        global_min_x = float("inf")
        global_min_y = float("inf")

        global_max_x = float("-inf")
        global_max_y = float("-inf")

        # Use tb3_0's resolution as the global map resolution.
        # Global map의 resolution은 tb3_0 map의 resolution을 사용한다.
        global_resolution = self.maps["tb3_0"]["resolution"]

        # -------------------------------------------------
        # Iterate over every robot map
        # 모든 Robot의 local map을 순회한다.
        # -------------------------------------------------
        for robot_name, map_info in self.maps.items():

            # Get the transform from robot map frame to world frame.
            # Robot의 map frame에서 world frame으로의 TF를 가져온다.
            transform = self.get_robot_world_transform(robot_name)

            if transform is None:
                continue

            # Extract translation from the TF.
            # TF에서 translation 정보를 가져온다.
            world_origin_x = transform.transform.translation.x
            world_origin_y = transform.transform.translation.y

            # Extract rotation and convert quaternion to yaw.
            # Quaternion rotation을 yaw angle로 변환한다.
            q = transform.transform.rotation

            _, _, yaw = euler_from_quaternion([
                q.x,
                q.y,
                q.z,
                q.w]
            )

            origin_x = map_info["origin_x"]
            origin_y = map_info["origin_y"]

            width = map_info["width"]
            height = map_info["height"]

            resolution = map_info["resolution"]

            # ---------------------------------------------
            # Four corners of local OccupancyGrid
            #
            # Local map의 네 모서리 좌표를 계산한다.
            # ---------------------------------------------
            corners = [
                (origin_x, origin_y),
                (origin_x + width * resolution, origin_y),
                (origin_x, origin_y + height * resolution),
                (
                    origin_x + width * resolution,
                    origin_y + height * resolution
                )
            ]

            world_corners = []

            # Transform each local corner into world coordinates.
            # 각 local corner를 world coordinate로 변환한다.
            for local_x, local_y in corners:

                world_x = (
                    world_origin_x
                    + local_x * math.cos(yaw)
                    - local_y * math.sin(yaw)
                )

                world_y = (
                    world_origin_y
                    + local_x * math.sin(yaw)
                    + local_y * math.cos(yaw)
                )

                world_corners.append(
                    (world_x, world_y)
                )

            # ---------------------------------------------
            # Calculate bounding box in world coordinates
            #
            # 모든 local map을 포함할 수 있는
            # global minimum / maximum 좌표를 계산한다.
            # ---------------------------------------------
            min_x = min(
                point[0] for point in world_corners
            )

            max_x = max(
                point[0] for point in world_corners
            )

            min_y = min(
                point[1] for point in world_corners
            )

            max_y = max(
                point[1] for point in world_corners
            )

            # Update global minimum coordinate
            # Global minimum coordinate를 갱신한다.
            global_min_x = min(global_min_x, min_x)
            global_min_y = min(global_min_y, min_y)

            # Update global maximum coordinate
            # Global maximum coordinate를 갱신한다.
            global_max_x = max(global_max_x, max_x)
            global_max_y = max(global_max_y, max_y)

        # =================================================
        # Step 2. Compute Global Map Size
        #
        # Bounding Box (meter)
        #          ↓
        # OccupancyGrid Size (cell)
        #
        # World coordinate의 실제 길이를
        # OccupancyGrid의 cell 개수로 변환한다.
        # =================================================

        # Physical size (meter)
        # Global map의 실제 물리적 크기(m)를 계산한다.
        world_width = global_max_x - global_min_x
        world_height = global_max_y - global_min_y

        # Number of cells
        #
        # ceil() is used so that the entire map
        # fits inside the global map.
        #
        # 전체 map이 global map 내부에 포함되도록
        # cell 개수를 올림하여 계산한다.
        global_width = int(np.ceil(world_width / global_resolution))
        global_height = int(np.ceil(world_height / global_resolution))

        self.get_logger().info(
            f"""
            Global Bounding Box

            min_x : {global_min_x:.2f}
            min_y : {global_min_y:.2f}

            max_x : {global_max_x:.2f}
            max_y : {global_max_y:.2f}
            """
        )

        self.get_logger().info(
            f"""
            Global Map Size

            world_width : {world_width:.2f} m
            world_height : {world_height:.2f} m

            global_width : {global_width} cells
            global_height : {global_height} cells
            """
        )

        # =================================================
        # Step 3. Create Empty Global OccupancyGrid
        #
        # Every cell is initialized as Unknown (-1)
        #
        # Global map을 Unknown(-1) 상태로 초기화한다.
        #
        #      -1  -1  -1  -1
        #      -1  -1  -1  -1
        #      -1  -1  -1  -1
        #
        # Local maps will be copied into this canvas.
        # 이후 각 Robot의 local map을 이 global canvas에 반영한다.
        # =================================================

        merged_map = np.full(
            (global_height, global_width),
            -1,
            dtype=np.int8
        )

        # =================================================
        # Step 4. Merge Each Local Map
        #
        # Process every robot's map independently.
        #
        # 각 Robot의 local map을 하나씩 global map에 반영한다.
        # =================================================
        for robot_name, map_info in self.maps.items():

            # Get the current transform for this robot.
            # 현재 Robot의 map → world TF를 가져온다.
            transform = self.get_robot_world_transform(robot_name)

            if transform is None:
                continue

            world_origin_x = transform.transform.translation.x
            world_origin_y = transform.transform.translation.y

            # Convert quaternion rotation to yaw.
            # Quaternion rotation을 yaw angle로 변환한다.
            q = transform.transform.rotation

            _, _, yaw = euler_from_quaternion([
                q.x,
                q.y,
                q.z,
                q.w]
            )

            # ---------------------------------------------
            # Local occupancy grid
            # ---------------------------------------------
            map_array = map_info["array"]

            width = map_info['width']
            height = map_info['height']
            resolution = map_info['resolution']

            origin_x = map_info['origin_x']
            origin_y = map_info['origin_y']

            # ---------------------------------------------
            # Visit every cell in local map
            #
            # Local OccupancyGrid의 모든 cell을 순회한다.
            # ---------------------------------------------
            for y in range(height):

                for x in range(width):

                    # Get the occupancy value of the current cell.
                    # 현재 cell의 occupancy value를 가져온다.
                    new_value = map_array[y, x]

                    # Convert cell index to local map coordinates.
                    # Cell index를 local map coordinate(m)로 변환한다.
                    local_x = origin_x + x * resolution
                    local_y = origin_y + y * resolution

                    # Apply the map rotation.
                    # Local map의 rotation을 적용한다.
                    rotated_x = (
                        local_x * math.cos(yaw)
                        - local_y * math.sin(yaw)
                    )

                    rotated_y = (
                        local_x * math.sin(yaw)
                        + local_y * math.cos(yaw)
                    )

                    # Translate the rotated point into world coordinates.
                    # Rotation된 local coordinate를 world coordinate로 변환한다.
                    world_x = world_origin_x + rotated_x
                    world_y = world_origin_y + rotated_y
                    
                    # ---------------------------------------------
                    # Convert world coordinate
                    # to merged map cell index
                    #
                    # World coordinate를 global merged map의
                    # cell index로 변환한다.
                    # ---------------------------------------------
                    map_x = int(
                        round(
                            (world_x - global_min_x)
                            / resolution
                        )
                    )

                    map_y = int(
                        round(
                            (world_y - global_min_y)
                            / resolution
                        )
                    )

                    # Ignore points outside the global map boundary.
                    # Global map 범위를 벗어난 cell은 무시한다.
                    if map_x < 0 or map_x >= global_width:
                        continue

                    if map_y < 0 or map_y >= global_height:
                        continue

                    # Existing value inside merged map
                    # 현재 global map cell에 저장되어 있는 값을 가져온다.
                    old_value = merged_map[
                        map_y,
                        map_x
                    ]

                    # -------------------------------------
                    # Ignore Unknown cells
                    #
                    # Unknown(-1)은 기존의 known information을
                    # 덮어쓰지 않도록 무시한다.
                    # -------------------------------------
                    if new_value == -1:
                        continue

                    # -------------------------------------
                    # Preserve Occupied cells.
                    #
                    # 이미 Occupied(100)인 cell은
                    # 다른 map의 값으로 덮어쓰지 않는다.
                    # -------------------------------------
                    if old_value == 100:
                        continue

                    # -------------------------------------
                    # Update merged map.
                    #
                    # Free(0) 또는 Occupied(100) 등의
                    # 새로운 occupancy information을 반영한다.
                    # -------------------------------------
                    merged_map[
                        map_y,
                        map_x
                    ] = new_value

            self.get_logger().info(
                "Merged Map Published"
            )

        # =================================================
        # Create the final OccupancyGrid message
        #
        # 계산된 NumPy merged map을 ROS2 OccupancyGrid
        # message로 변환한다.
        # =================================================
        merged_msg = OccupancyGrid()

        # Global merged map uses the world coordinate frame.
        # 최종 merged map은 global world frame을 사용한다.
        merged_msg.header.frame_id = "world"

        merged_msg.header.stamp = (
            self.get_clock().now().to_msg()
        )

        # Set map resolution and dimensions.
        # Global map의 resolution과 크기를 설정한다.
        merged_msg.info.resolution = global_resolution
        merged_msg.info.width = global_width
        merged_msg.info.height = global_height

        # Set the origin of the global map.
        # Global map의 origin을 설정한다.
        merged_msg.info.origin.position.x = global_min_x
        merged_msg.info.origin.position.y = global_min_y
        merged_msg.info.origin.position.z = 0.0

        # Global map has no additional rotation.
        # Global map 자체에는 별도의 rotation을 적용하지 않는다.
        merged_msg.info.origin.orientation.x = 0.0
        merged_msg.info.origin.orientation.y = 0.0
        merged_msg.info.origin.orientation.z = 0.0
        merged_msg.info.origin.orientation.w = 1.0

        # Convert the 2D NumPy array back to a 1D ROS OccupancyGrid data array.
        # 2D NumPy array를 ROS2 OccupancyGrid의 1D data array로 변환한다.
        merged_msg.data = merged_map.flatten().tolist()

        # Publish the global merged map.
        # 최종 global merged map을 /merged_map topic으로 publish한다.
        self.map_pub.publish(merged_msg)


def main(args=None):

    # Initialize ROS2
    # ROS2 communication을 초기화한다.
    rclpy.init(args=args)

    # Create node
    # MapMergeNode를 생성한다.
    node = MapMergeNode()

    # Start callback loop
    # ROS2 callback을 실행하여 map과 TF 정보를 계속 처리한다.
    rclpy.spin(node)

    # Destroy node before shutdown
    # ROS2 종료 전에 Node를 제거한다.
    node.destroy_node()

    # Shutdown ROS2
    # ROS2 communication을 종료한다.
    rclpy.shutdown()


# Program Entry Point
# Python script를 직접 실행할 경우 main()을 실행한다.
if __name__ == "__main__":
    main()
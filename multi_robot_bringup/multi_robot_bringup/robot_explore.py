import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
import math


class RobotExplore(Node):
    def __init__(self):
        # Initialize the ROS2 node
        # ROS2 Node를 초기화한다.
        super().__init__('robot_explore')

        # Subscribe to the LiDAR scan topic
        # LiDAR scan topic을 subscribe하여 주변 장애물 정보를 수신한다.
        self.scan_sub = self.create_subscription(
            LaserScan,
            'scan',
            self.scan_callback,
            10
        )

        # Publish velocity commands to control the robot
        # Robot의 이동을 제어하기 위한 velocity command를 publish한다.
        self.cmd_pub = self.create_publisher(
            Twist,
            'cmd_vel',
            10
        )

        # Store the latest LiDAR scan
        # 가장 최근에 수신한 LiDAR 데이터를 저장한다.
        self.scan = None

        # Run the control loop at 10 Hz
        # 0.1초마다 control loop를 실행하여 10 Hz로 Robot을 제어한다.
        self.timer = self.create_timer(
            0.1,
            self.control_loop
        )

    def get_front_distance(self):
        # Initialize the minimum front distance as infinity
        # 정면에서 측정된 최소 거리를 infinity로 초기화한다.
        front_distance = float('inf')

        # Process all LiDAR range measurements
        # 전체 LiDAR range measurement를 순회한다.
        for i, distance in enumerate(self.scan.ranges):
            # Calculate the angle corresponding to each LiDAR measurement
            # 각 LiDAR measurement에 해당하는 angle을 계산한다.
            angle = self.scan.angle_min + i * self.scan.angle_increment

            # Use the front region within ±30 degrees
            # Robot 정면 기준 ±30도 영역을 사용한다.
            if angle <= math.radians(30) or angle >= math.radians(330):

                # Ignore invalid measurements such as inf
                # inf와 같은 유효하지 않은 measurement는 제외한다.
                if math.isfinite(distance):
                    front_distance = min(front_distance, distance)

        return front_distance

    def get_left_distance(self):
        # Initialize the minimum left distance as infinity
        # 왼쪽에서 측정된 최소 거리를 infinity로 초기화한다.
        left_distance = float('inf')

        # Process all LiDAR range measurements
        # 전체 LiDAR range measurement를 순회한다.
        for i, distance in enumerate(self.scan.ranges):
            # Calculate the angle corresponding to each measurement
            # 각 measurement에 해당하는 angle을 계산한다.
            angle = self.scan.angle_min + i * self.scan.angle_increment

            # Use the left-side region from 30 to 150 degrees
            # Robot 기준 왼쪽 영역인 30~150도 범위를 사용한다.
            if math.radians(30) < angle < math.radians(150):

                # Ignore invalid measurements
                # 유효하지 않은 measurement는 제외한다.
                if math.isfinite(distance):
                    left_distance = min(left_distance, distance)

        return left_distance

    def get_right_distance(self):
            # Initialize the minimum right distance as infinity
            # 오른쪽에서 측정된 최소 거리를 infinity로 초기화한다.
            right_distance = float('inf')
    
            # Process all LiDAR range measurements
            # 전체 LiDAR range measurement를 순회한다.
            for i, distance in enumerate(self.scan.ranges):
                # Calculate the angle corresponding to each measurement
                # 각 measurement에 해당하는 angle을 계산한다.
                angle = self.scan.angle_min + i * self.scan.angle_increment
    
                # Use the right-side region from 210 to 330 degrees
                # Robot 기준 오른쪽 영역인 210~330도 범위를 사용한다.
                if math.radians(210) < angle < math.radians(330):

                    # Ignore invalid measurements
                    # 유효하지 않은 measurement는 제외한다.
                    if math.isfinite(distance):
                        right_distance = min(right_distance, distance)
    
            return right_distance

    def control_loop(self):
        # Wait until the first LiDAR message is received
        # 첫 번째 LiDAR message를 수신하기 전에는 control을 수행하지 않는다.
        if self.scan is None:
            return

        # Calculate the minimum distance in each direction
        # Front, Left, Right 방향의 최소 거리를 계산한다.
        front_distance = self.get_front_distance()
        left_distance = self.get_left_distance()
        right_distance = self.get_right_distance()

        # Create a velocity command
        # Robot에 전달할 velocity command를 생성한다.
        cmd = Twist()

        # Move forward when there is enough space in front
        # 정면에 충분한 공간이 있으면 전진한다.
        if front_distance > 0.6:
            cmd.linear.x = 0.15
            cmd.angular.z = 0.0

        # Stop forward motion when an obstacle is detected
        # 장애물이 일정 거리 이내에 접근하면 전진을 멈춘다.
        else:
            cmd.linear.x = 0.0

            # Turn toward the side with more available space
            # 좌우 거리를 비교하여 더 넓은 방향으로 회전한다.
            if left_distance > right_distance:
                # Turn left
                # 왼쪽 방향으로 회전한다.
                cmd.angular.z = 0.6
            else:
                # Turn right
                # 오른쪽 방향으로 회전한다.
                cmd.angular.z = -0.6

        # Publish the velocity command
        # 계산된 velocity command를 Robot에 전달한다.
        self.cmd_pub.publish(cmd)

        # Print the current LiDAR distances for monitoring
        # 현재 LiDAR 거리값을 출력하여 Robot의 상태를 확인한다.
        self.get_logger().info(
            f'front : {front_distance:.2f}'
            f'left : {left_distance:.2f}'
            f'right : {right_distance:.2f}'
        )

    def scan_callback(self, msg):
        # Store the latest LaserScan message
        # 가장 최근에 수신한 LaserScan message를 저장한다.
        self.scan = msg


def main(args=None):
    # Initialize the ROS2 communication system
    # ROS2 communication을 초기화한다.
    rclpy.init(args=args)

    # Create the RobotExplore node
    # RobotExplore Node를 생성한다.
    node = RobotExplore()

    try:
        # Keep the node running and process incoming messages
        # Node를 실행하면서 incoming message를 계속 처리한다.
        rclpy.spin(node)

    except KeyboardInterrupt:
        # Allow the node to terminate safely with Ctrl+C
        # Ctrl+C 입력 시 안전하게 종료한다.
        pass

    finally:
        # Destroy the node and shut down ROS2
        # Node를 제거하고 ROS2를 종료한다.
        node.destroy_node()
        rclpy.shutdown()


# Run main() when this file is executed directly
# 이 파일을 직접 실행할 경우 main()을 호출한다.
if __name__ == '__main__':
    main()
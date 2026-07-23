# Part 6. Multi-Robot SLAM
# Single Robot SLAM Verification in a Multi-Robot Environment

---

# Objective | 실습 목표

## English

The objective of this lab was to integrate SLAM Toolbox into the previously implemented multi-robot Gazebo environment.

Instead of immediately launching SLAM for all robots, the goal was to first verify that a single robot (`tb3_0`) could successfully perform SLAM inside a namespaced multi-robot environment.

During this process, several ROS2 namespace and TF issues were identified and resolved.

## 한국어

이번 실습의 목표는 기존에 구축한 Multi-Robot Gazebo 환경에 SLAM Toolbox를 통합하는 것이다.

처음부터 모든 로봇에서 SLAM을 실행하는 것이 아니라, 먼저 하나의 로봇(`tb3_0`)이 Multi-Robot 환경에서 정상적으로 SLAM을 수행하는지 검증하였다.

이 과정에서 ROS2 Namespace와 TF 관련 문제를 해결하였다.

---

# What is SLAM Toolbox?

## English

SLAM Toolbox is a ROS2 package that performs Simultaneous Localization and Mapping (SLAM).

It estimates the robot's pose while simultaneously constructing an occupancy grid map using:

- LaserScan
- Odometry
- TF

Unlike Cartographer, SLAM Toolbox provides flexible online mapping and pose graph optimization, making it suitable for long-term mapping applications.

## 한국어

SLAM Toolbox는 ROS2에서 사용하는 대표적인 Simultaneous Localization and Mapping(SLAM) 패키지이다.

다음 정보를 이용하여

- LaserScan
- Odometry
- TF

로봇의 위치를 추정하면서 동시에 Occupancy Grid Map을 생성한다.

---

# Why is Multi-Robot SLAM Difficult?

## English

Running multiple SLAM nodes is not simply a matter of launching multiple instances.

Each robot must have completely independent:

- namespace
- TF frames
- scan topic
- map frame
- odom frame
- base frame

Otherwise, robots will interfere with each other's localization and mapping process.

## 한국어

Multi-Robot 환경에서는 단순히 SLAM 노드를 여러 개 실행한다고 동작하지 않는다.

각 로봇은 서로 독립적인

- Namespace
- TF Frame
- Scan Topic
- Map Frame
- Odom Frame
- Base Frame

을 가져야 한다.

그렇지 않으면 각 로봇의 지도와 위치 정보가 서로 충돌하게 된다.

---

# Step 1. Create a Separate SLAM Launch File

Instead of modifying the Gazebo launch file, a dedicated launch file was created.

```
multi_robot_bringup

launch/
    gaze.launch.py
    multi_slam.launch.py
```

This separates

- Gazebo
- Robot Spawn
- Robot State Publisher

from

- SLAM

making debugging much easier.

---

# Step 2. Launch SLAM for Only One Robot

Initially, only one robot was launched.

```python
Node(
    package="slam_toolbox",
    executable="async_slam_toolbox_node",
    namespace="tb3_0",
    name="slam_toolbox"
)
```

The objective was to verify

- Namespace
- Topics
- TF

before expanding to multiple robots.

---

# Step 3. Problem 1
# SLAM did not subscribe to LaserScan

Checking

```bash
ros2 topic info /tb3_0/scan
```

showed

```
Publisher : 1
Subscriber : 0
```

meaning that SLAM Toolbox was not receiving LaserScan.

---

# Cause Analysis

Although the SLAM node was launched inside

```
namespace = tb3_0
```

the parameter

```
scan_topic
```

was still configured as

```
/scan
```

Absolute topic names beginning with `/` ignore namespaces.

Therefore

```
SLAM

Subscribe

/scan
```

while the actual topic was

```
/tb3_0/scan
```

---

# Step 4. Fix scan_topic

Before modifying the launch file, the current parameter was verified.

```bash
ros2 param get /tb3_0/slam_toolbox scan_topic
```

Result

```
/scan
```

This confirmed that SLAM Toolbox was subscribing to the default absolute topic instead of the namespaced LaserScan topic.

The parameter was then overridden inside the launch file.

```python
parameters=[
{
    "use_sim_time": True,
    "scan_topic": "/tb3_0/scan"
}
]
```

After restarting the node, the updated parameter was verified.

```bash
ros2 param get /tb3_0/slam_toolbox scan_topic
```

Result

```
/tb3_0/scan
```

Finally, the topic connection was confirmed.

```bash
ros2 topic info /tb3_0/scan
```

Result

```
Publisher : 1
Subscriber : 1
```

The SLAM node successfully subscribed to the LaserScan topic.

---

# Step 5. Problem 2
# Map Frame Did Not Exist

RViz did not show

```
map
```

as a Fixed Frame.

Running

```bash
ros2 run tf2_tools view_frames
```

showed

```
world
 └── tb3_0/odom
      └── tb3_0/base_footprint
```

There was no

```
map
```

frame.

---

# Cause Analysis

SLAM Toolbox still expected

```
odom
base_footprint
```

while the actual TF tree used

```
tb3_0/odom
tb3_0/base_footprint
```

The frame names did not match.

---

# Step 6. Configure Frame Parameters

Before updating the launch file, the TF tree was inspected.

```bash
ros2 run tf2_tools view_frames
```

The generated TF tree contained

```
world
 └── tb3_0/odom
      └── tb3_0/base_footprint
```

but the `tb3_0/map` frame was missing.

The current frame parameters were then verified.

```bash
ros2 param get /tb3_0/slam_toolbox odom_frame
ros2 param get /tb3_0/slam_toolbox base_frame
ros2 param get /tb3_0/slam_toolbox map_frame
```

Result

```
odom
base_footprint
map
```

This confirmed that SLAM Toolbox was using the default frame names instead of the namespaced TF frames.

The launch file was then updated.

```python
parameters=[
{
    "use_sim_time": True,
    "scan_topic": "/tb3_0/scan",
    "odom_frame": "tb3_0/odom",
    "base_frame": "tb3_0/base_footprint",
    "map_frame": "tb3_0/map"
}
]
```

After restarting the node, the updated parameters were verified.

```bash
ros2 param get /tb3_0/slam_toolbox odom_frame
ros2 param get /tb3_0/slam_toolbox base_frame
ros2 param get /tb3_0/slam_toolbox map_frame
```

Result

```
tb3_0/odom
tb3_0/base_footprint
tb3_0/map
```

RViz then recognized

```
tb3_0/map
```

as a valid Fixed Frame.

The Occupancy Grid was further verified using

```bash
ros2 topic echo /map --once
```

Result

```
frame_id: tb3_0/map
```

confirming that SLAM Toolbox was publishing the map using the correct frame.

---

# Step 7. Verify Occupancy Grid

Checking

```bash
ros2 topic echo /map --once
```

confirmed

```
frame_id

tb3_0/map
```

indicating that OccupancyGrid messages were successfully generated.

---

# Step 8. Analyze LaserScan Data

LaserScan data contained mostly

```
inf
```

values with only a few finite ranges.

Example

```
inf
inf
inf
2.79
inf
```

This indicates that the sensor was functioning correctly, but there were very few obstacles in the simulation environment.

---

# Why Was the Map Almost Empty?

The current Gazebo world contains almost no obstacles.

SLAM requires environmental features such as

- walls
- corners
- obstacles

to perform scan matching and build a meaningful occupancy grid.

Therefore the resulting map remained nearly empty even though SLAM was operating correctly.

---

# Data Flow

```
Gazebo

↓

Laser Plugin

↓

/tb3_0/scan

↓

SLAM Toolbox

↓

Occupancy Grid

↓

/map

↓

RViz
```

---

# Key Takeaways

- SLAM Toolbox does not automatically adapt absolute topic names to namespaces.
- scan_topic must be configured explicitly in a multi-robot environment.
- TF frame names must match the robot namespace.
- OccupancyGrid generation was successfully verified.
- Empty environments are not suitable for evaluating SLAM performance.

---

# Next Step

Implement multiple SLAM Toolbox instances.

```
tb3_0/slam_toolbox

tb3_1/slam_toolbox

tb3_2/slam_toolbox
```

using a loop inside

```
multi_slam.launch.py
```

so that each robot independently performs SLAM with its own namespace and TF tree.

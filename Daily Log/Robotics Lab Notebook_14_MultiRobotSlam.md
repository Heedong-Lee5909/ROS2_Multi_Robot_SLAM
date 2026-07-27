# Part 6. Multi-Robot SLAM
# Multiple SLAM Toolbox Instances in a Multi-Robot Environment

---

# Objective | 실습 목표

## English

The objective of this lab was to extend the previously verified single-robot SLAM configuration to all three TurtleBot3 robots.

Each robot runs an independent SLAM Toolbox instance using its own:

- Namespace
- LaserScan topic
- TF frames
- Occupancy Grid Map

The goal was to verify that `tb3_0`, `tb3_1`, and `tb3_2` could independently generate occupancy grid maps without interfering with each other.

## 한국어

이번 실습의 목표는 이전 단계에서 `tb3_0`을 대상으로 검증한 SLAM 구성을 3대의 TurtleBot3 전체로 확장하는 것이다.

각 Robot은 독립적인 SLAM Toolbox Instance를 실행하며 각각의

- Namespace
- LaserScan Topic
- TF Frame
- Occupancy Grid Map

을 사용하도록 구성하였다.

최종적으로 `tb3_0`, `tb3_1`, `tb3_2`가 서로 간섭하지 않고 각각 독립적으로 Occupancy Grid Map을 생성하는지 검증하였다.

---

# Step 1. Launch Multiple SLAM Toolbox Instances

The SLAM configuration previously verified with `tb3_0` was extended to all three robots.

Each robot was assigned its own SLAM Toolbox node.

```text
/tb3_0/slam_toolbox
/tb3_1/slam_toolbox
/tb3_2/slam_toolbox
```

The running SLAM nodes were verified using:

```bash
ros2 node list | grep slam
```

Result:

```text
/tb3_0/slam_toolbox
/tb3_1/slam_toolbox
/tb3_2/slam_toolbox
```

This confirmed that three independent SLAM Toolbox instances were running.

## 한국어

기존에 `tb3_0`에서 검증한 SLAM 구성을 3대의 Robot으로 확장하였다.

각 Robot은 자신의 Namespace 내부에서 독립적인 SLAM Toolbox Node를 실행한다.

```text
tb3_0 → /tb3_0/slam_toolbox
tb3_1 → /tb3_1/slam_toolbox
tb3_2 → /tb3_2/slam_toolbox
```

`ros2 node list`를 통해 3개의 SLAM Toolbox Node가 정상적으로 실행되고 있음을 확인하였다.

---

# Step 2. Verify LaserScan Connections

Each SLAM Toolbox instance must receive LaserScan data from its corresponding robot.

The LaserScan connections were checked using:

```bash
ros2 topic info /tb3_0/scan
ros2 topic info /tb3_1/scan
ros2 topic info /tb3_2/scan
```

Result for each robot:

```text
Publisher count: 1
Subscription count: 1
```

The publisher corresponds to the Gazebo LaserScan plugin, while the subscriber corresponds to the SLAM Toolbox instance.

Therefore, the sensor data flow was successfully separated by namespace.

## 한국어

각 SLAM Toolbox는 해당 Robot의 LaserScan Topic만 Subscribe해야 한다.

각 `/scan` Topic을 확인한 결과 모든 Robot에서

```text
Publisher : 1
Subscriber : 1
```

이 확인되었다.

따라서 다음과 같이 각 Robot의 LaserScan이 독립적인 SLAM Toolbox로 정상 전달되고 있음을 확인하였다.

```text
/tb3_0/scan → /tb3_0/slam_toolbox
/tb3_1/scan → /tb3_1/slam_toolbox
/tb3_2/scan → /tb3_2/slam_toolbox
```

---

# Step 3. Verify Independent Map Topics

After launching all three SLAM Toolbox instances, the generated map topics were checked.

```bash
ros2 topic list | grep map
```

Result:

```text
/tb3_0/map
/tb3_0/map_metadata

/tb3_1/map
/tb3_1/map_metadata

/tb3_2/map
/tb3_2/map_metadata
```

Each robot successfully generated its own Occupancy Grid Map topic.

## 한국어

3개의 SLAM Toolbox를 실행한 후 각 Robot의 Map Topic을 확인하였다.

각 Robot마다 독립적인

```text
/map
/map_metadata
```

Topic이 생성되었다.

따라서 하나의 `/map` Topic을 공유하는 것이 아니라 각 Robot이 자신의 Namespace 내부에서 독립적인 지도를 생성하도록 구성되었음을 확인하였다.

---

# Step 4. Verify Map Frame IDs

The frame ID of each Occupancy Grid was checked.

```bash
ros2 topic echo /tb3_0/map --once | head -n 6
ros2 topic echo /tb3_1/map --once | head -n 6
ros2 topic echo /tb3_2/map --once | head -n 6
```

Results:

```text
/tb3_0/map
frame_id: tb3_0/map
```

```text
/tb3_1/map
frame_id: tb3_1/map
```

```text
/tb3_2/map
frame_id: tb3_2/map
```

This confirmed that each Occupancy Grid was associated with the correct namespaced map frame.

## 한국어

각 Occupancy Grid가 올바른 Map Frame을 사용하는지 확인하였다.

확인 결과:

```text
/tb3_0/map → tb3_0/map
/tb3_1/map → tb3_1/map
/tb3_2/map → tb3_2/map
```

으로 구성되어 있었다.

따라서 각 Robot의 Occupancy Grid와 TF Frame이 Namespace 기준으로 정상적으로 분리되어 있음을 확인하였다.

---

# Step 5. Verify SLAM TF Transform

The transform between each robot's map frame and base frame was verified using `tf2_echo`.

Example:

```bash
ros2 run tf2_ros tf2_echo tb3_0/map tb3_0/base_footprint
```

The transform was successfully returned.

The same verification was performed for the other robots.

```bash
ros2 run tf2_ros tf2_echo tb3_1/map tb3_1/base_footprint
ros2 run tf2_ros tf2_echo tb3_2/map tb3_2/base_footprint
```

The initial message could temporarily show:

```text
Invalid frame ID
```

or

```text
Lookup would require extrapolation into the past
```

while the TF buffer was being initialized.

After TF data became available, continuous transforms were successfully returned.

## 한국어

각 Robot의 SLAM TF Chain이 정상적으로 연결되어 있는지 `tf2_echo`를 이용하여 확인하였다.

예를 들어:

```bash
ros2 run tf2_ros tf2_echo tb3_0/map tb3_0/base_footprint
```

을 실행하여

```text
tb3_0/map
    ↓
tb3_0/odom
    ↓
tb3_0/base_footprint
```

사이의 Transform이 정상적으로 계산되는 것을 확인하였다.

초기 실행 시 TF Buffer가 아직 충분히 구성되지 않아 `Invalid frame ID` 또는 과거 시점의 Transform을 찾을 수 없다는 메시지가 일시적으로 발생했지만, 이후 정상적으로 Transform 값이 출력되었다.

---

# Step 6. Inspect the Complete TF Tree

The complete TF structure was inspected using:

```bash
ros2 run tf2_tools view_frames
```

The resulting TF tree showed three independent SLAM TF chains.

```text
tb3_0/map
    ↓
tb3_0/odom
    ↓
tb3_0/base_footprint
    ↓
tb3_0/base_link
```

```text
tb3_1/map
    ↓
tb3_1/odom
    ↓
tb3_1/base_footprint
    ↓
tb3_1/base_link
```

```text
tb3_2/map
    ↓
tb3_2/odom
    ↓
tb3_2/base_footprint
    ↓
tb3_2/base_link
```

SLAM Toolbox was publishing the `map → odom` transform independently for each robot.

## 한국어

전체 TF Tree를 확인한 결과 3개의 독립적인 TF Chain이 생성되어 있었다.

각 SLAM Toolbox는 자신의 Namespace에서

```text
map → odom
```

Transform을 생성하고 있었으며, Gazebo의 Odometry 및 Robot State Publisher가 생성하는 TF와 연결되어 각각 하나의 Robot TF Tree를 구성하였다.

즉 현재 시스템에는 다음과 같은 3개의 독립적인 SLAM 좌표계가 존재한다.

```text
tb3_0/map → tb3_0/odom → tb3_0/base_footprint
tb3_1/map → tb3_1/odom → tb3_1/base_footprint
tb3_2/map → tb3_2/odom → tb3_2/base_footprint
```

---

# Step 7. Problem
# RViz Displayed "No map received"

Although the map topics were being published correctly, RViz sometimes displayed:

```text
Status: Warn
Message: No map received
```

for the namespaced map topics.

The map itself was first verified from the terminal.

```bash
ros2 topic echo /tb3_0/map --once
```

Example:

```text
frame_id: tb3_0/map

resolution: 0.05
width: 40
height: 40
```

Therefore, SLAM Toolbox was successfully generating Occupancy Grid messages.

---

# Step 8. Verify Map Publishing Rate

To determine whether the map was continuously being published, the publishing frequency was measured.

```bash
ros2 topic hz /tb3_0/map
ros2 topic hz /tb3_1/map
ros2 topic hz /tb3_2/map
```

Result:

```text
average rate: 0.100
```

for all three robots.

This means that each SLAM Toolbox instance was publishing its Occupancy Grid approximately once every 10 seconds.

## 한국어

RViz에서 Map이 표시되지 않는 원인이 SLAM Toolbox의 Map Publish 중단 때문인지 확인하기 위해 각 `/map` Topic의 Publish Rate를 측정하였다.

3개의 Map Topic 모두:

```text
0.100 Hz
```

로 측정되었다.

즉 약 10초마다 새로운 Occupancy Grid가 정상적으로 Publish되고 있음을 확인하였다.

---

# Step 9. Analyze ROS2 QoS

The QoS configuration of the map topic was inspected using:

```bash
ros2 topic info /tb3_1/map --verbose
```

The SLAM Toolbox publisher used:

```text
Reliability: RELIABLE
Durability: TRANSIENT_LOCAL
```

RViz was also confirmed as a subscriber to the map topic.

The RViz Map Display was therefore configured as:

```text
Reliability Policy = Reliable
Durability Policy  = Transient Local
```

After configuring the durability policy, RViz successfully received the Occupancy Grid.

```text
Status: Ok
Message: Map received
Map: Map OK
Transform: Ok
```

## 한국어

`ros2 topic info --verbose`를 이용하여 Map Topic의 QoS 설정을 확인하였다.

SLAM Toolbox의 Map Publisher는:

```text
Reliability = RELIABLE
Durability  = TRANSIENT_LOCAL
```

을 사용하고 있었다.

따라서 RViz Map Display에서도 다음과 같이 설정하였다.

```text
Reliability Policy = Reliable
Durability Policy  = Transient Local
```

설정 후 RViz에서:

```text
Map received
Map OK
Transform OK
```

상태를 확인하였다.

`TRANSIENT_LOCAL`은 늦게 Topic에 연결된 Subscriber가 Publisher가 보관하고 있는 최근 데이터를 받을 수 있도록 하는 Durability 정책이다.

---

# Step 10. Verify Map Reception with Matching QoS

To separate the RViz issue from the ROS2 communication itself, the Occupancy Grid was directly subscribed to using the same QoS settings.

```bash
ros2 topic echo /tb3_0/map \
  --qos-reliability reliable \
  --qos-durability transient_local \
  --once
```

Result:

```text
frame_id: tb3_0/map

resolution: 0.05
width: 40
height: 40
```

The Occupancy Grid was successfully received.

This confirmed that the SLAM Toolbox publisher and ROS2 communication were operating correctly.

## 한국어

RViz 문제와 ROS2 Topic 통신 문제를 분리하여 확인하기 위해 동일한 QoS 조건으로 직접 `/map` Topic을 Subscribe하였다.

Occupancy Grid가 정상적으로 수신되었으며:

```text
frame_id
resolution
width
height
occupancy data
```

가 정상적으로 출력되었다.

따라서 SLAM Toolbox의 Map 생성 및 ROS2 Topic 통신 자체에는 문제가 없음을 확인하였다.

---

# Step 11. Verify RViz Subscriptions for All Robots

With three Map Displays configured in RViz, each map topic was inspected using:

```bash
ros2 topic info /tb3_0/map --verbose
ros2 topic info /tb3_1/map --verbose
ros2 topic info /tb3_2/map --verbose
```

For all three topics, RViz appeared as an active subscriber.

Example:

```text
Node name: rviz
Endpoint type: SUBSCRIPTION

Reliability: RELIABLE
Durability: TRANSIENT_LOCAL
```

This confirmed that RViz had successfully created subscriptions for all three Occupancy Grid topics.

## 한국어

RViz에서 여러 Map Display를 구성한 상태에서 각 `/map` Topic의 Subscriber를 확인하였다.

3개의 Topic 모두 `/rviz` Node가 Subscriber로 연결되어 있었으며 QoS 또한:

```text
RELIABLE
TRANSIENT_LOCAL
```

로 설정되어 있음을 확인하였다.

---

# Step 12. Verify Independent Mapping with Teleoperation

After confirming the SLAM nodes, topics, TF frames, and QoS configuration, each robot was manually moved to verify actual map generation.

## tb3_0

```bash
ros2 run turtlebot3_teleop teleop_keyboard \
  --ros-args -r cmd_vel:=/tb3_0/cmd_vel
```

RViz:

```text
Fixed Frame = tb3_0/map
Map Topic   = /tb3_0/map
```

The occupancy grid expanded as `tb3_0` moved through the environment.

---

## tb3_1

```bash
ros2 run turtlebot3_teleop teleop_keyboard \
  --ros-args -r cmd_vel:=/tb3_1/cmd_vel
```

RViz:

```text
Fixed Frame = tb3_1/map
Map Topic   = /tb3_1/map
```

The occupancy grid generated by `tb3_1` was independently updated.

---

## tb3_2

```bash
ros2 run turtlebot3_teleop teleop_keyboard \
  --ros-args -r cmd_vel:=/tb3_2/cmd_vel
```

RViz:

```text
Fixed Frame = tb3_2/map
Map Topic   = /tb3_2/map
```

The occupancy grid generated by `tb3_2` was also successfully updated.

## 한국어

마지막으로 각 Robot을 Teleoperation으로 직접 이동시켜 실제 Mapping이 수행되는지 확인하였다.

각 Robot을 개별적으로 이동시켰을 때 해당 Robot의 Occupancy Grid가 이동 경로와 LaserScan 측정 결과에 따라 확장되는 것을 확인하였다.

따라서:

```text
tb3_0 → Independent SLAM ✓
tb3_1 → Independent SLAM ✓
tb3_2 → Independent SLAM ✓
```

3대의 Robot 모두 독립적인 SLAM을 정상적으로 수행하였다.

---

# Multi-Robot Independent SLAM Data Flow

```text
tb3_0
Gazebo
   │
   ▼
/tb3_0/scan
   │
   ▼
/tb3_0/slam_toolbox
   │
   ├──► /tb3_0/map
   │
   └──► tb3_0/map → tb3_0/odom


tb3_1
Gazebo
   │
   ▼
/tb3_1/scan
   │
   ▼
/tb3_1/slam_toolbox
   │
   ├──► /tb3_1/map
   │
   └──► tb3_1/map → tb3_1/odom


tb3_2
Gazebo
   │
   ▼
/tb3_2/scan
   │
   ▼
/tb3_2/slam_toolbox
   │
   ├──► /tb3_2/map
   │
   └──► tb3_2/map → tb3_2/odom
```

Each robot currently maintains its own independent SLAM coordinate system and Occupancy Grid.

각 Robot은 현재 자신의 독립적인 SLAM 좌표계와 Occupancy Grid를 유지한다.

---

# Current System Architecture

```text
                  Multi-Robot Gazebo
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
        tb3_0          tb3_1          tb3_2
          │              │              │
        /scan          /scan          /scan
          │              │              │
          ▼              ▼              ▼
    SLAM Toolbox    SLAM Toolbox    SLAM Toolbox
          │              │              │
          ▼              ▼              ▼
   /tb3_0/map      /tb3_1/map      /tb3_2/map
```

At this stage, the three maps are independent and have not yet been combined into a shared global map.

현재 단계에서는 3개의 Robot이 각각 독립적인 Map을 생성하며, 아직 하나의 Global Map으로 통합되지는 않았다.

---

# Key Takeaways

## English

- Three independent SLAM Toolbox instances were successfully executed.
- Each robot uses its own namespaced LaserScan topic.
- Each robot generates an independent Occupancy Grid Map.
- Each robot maintains its own `map → odom → base_footprint` TF chain.
- `ros2 topic info`, `ros2 topic echo`, `ros2 topic hz`, `ros2 param get`, `tf2_echo`, and `view_frames` were used to verify the SLAM pipeline.
- RViz Map Display QoS must be configured appropriately when visualizing SLAM Toolbox maps.
- All three robots successfully performed independent mapping.
- The current implementation is independent multi-robot SLAM, not yet a shared global map.

## 한국어

- 3개의 독립적인 SLAM Toolbox Instance를 정상적으로 실행하였다.
- 각 Robot은 자신의 Namespace가 적용된 LaserScan Topic을 사용한다.
- 각 Robot은 독립적인 Occupancy Grid Map을 생성한다.
- 각 Robot은 독립적인 `map → odom → base_footprint` TF Chain을 가진다.
- `ros2 topic info`, `ros2 topic echo`, `ros2 topic hz`, `ros2 param get`, `tf2_echo`, `view_frames` 등을 이용하여 SLAM Pipeline을 단계적으로 검증하였다.
- RViz에서 SLAM Toolbox Map을 표시할 때 QoS 설정을 확인해야 한다.
- `tb3_0`, `tb3_1`, `tb3_2` 모두 실제 Mapping이 정상적으로 수행되는 것을 확인하였다.
- 현재 구현은 각 Robot이 독립적인 Map을 생성하는 단계이며 아직 하나의 Shared Global Map으로 통합하지 않았다.

---

# Next Step

The next step is to merge the three independently generated Occupancy Grid Maps.

```text
/tb3_0/map ──┐
             │
/tb3_1/map ──┼──► Map Merge ──► Global Map
             │
/tb3_2/map ──┘
```

The next lab will focus on:

- Map Merge package configuration
- Independent map discovery
- Relative map alignment
- Merged Occupancy Grid generation
- Global map visualization in RViz

다음 단계에서는 각 Robot이 생성한 독립적인 Occupancy Grid를 하나의 Global Map으로 통합하는 Multi-Robot Map Merging을 구현한다.

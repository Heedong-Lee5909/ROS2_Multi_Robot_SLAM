# Part 4. Single Robot SLAM using SLAM Toolbox

## Objective

After successfully building a dynamic multi-robot launch system, the next step is enabling autonomous map generation.

In this section, SLAM Toolbox is integrated with TurtleBot3 to estimate the robot pose while simultaneously constructing an occupancy grid map. The generated map is then saved for future autonomous navigation using Navigation2.

앞선 파트에서는 Dynamic Multi-Robot Launch System을 구축하여 여러 대의 Robot을 Gazebo와 RViz에서 정상적으로 생성하였다.

이번 파트에서는 SLAM Toolbox를 이용하여 Robot의 위치를 추정하면서 동시에 지도를 생성하고, 생성된 지도를 저장하여 이후 Navigation2에서 활용할 수 있도록 구성한다.

---

# 1. What is SLAM?

SLAM (Simultaneous Localization And Mapping) is a technique that simultaneously estimates the robot pose and constructs a map of an unknown environment.

SLAM(Simultaneous Localization And Mapping)은 Robot의 위치를 추정(Localization)하면서 동시에 지도(Mapping)를 생성하는 기술이다.

---

# 2. Why is SLAM Needed?

Autonomous navigation requires both an environment map and the robot's current position.

Since neither information is available in an unknown environment, SLAM performs localization and mapping simultaneously.

자율주행을 위해서는 Robot의 현재 위치와 주변 지도가 모두 필요하다.

하지만 미지의 환경에서는 두 정보를 모두 알 수 없기 때문에 SLAM을 통해 위치 추정과 지도 생성을 동시에 수행한다.

---

# 3. SLAM Input and Output

SLAM Toolbox estimates the robot pose using sensor data and continuously updates the environment map.

SLAM Toolbox는 센서 데이터와 Robot의 이동 정보를 이용하여 현재 위치를 추정하고 지도를 생성한다.

### Input

- LaserScan (`/scan`)
- Odometry (`/odom`)
- TF (`/tf`)

### Output

- Occupancy Grid Map (`/map`)
- TF (`map → odom`)

---

# 4. Launching SLAM Toolbox

SLAM Toolbox was launched together with the TurtleBot3 simulation.

SLAM Toolbox를 TurtleBot3 Simulation과 함께 실행하였다.

```bash
export TURTLEBOT3_MODEL=burger

ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py

ros2 launch slam_toolbox online_async_launch.py
```

RViz was configured as follows.

- Fixed Frame = `map`
- Map
- LaserScan
- TF
- RobotModel

The Map Display Topic was changed to `/map` to visualize the generated occupancy grid.

RViz의 Fixed Frame을 `map`으로 설정하고 Map Topic을 `/map`으로 변경하여 생성된 지도를 확인하였다.

---

# 5. Generating an Occupancy Grid Map

The robot was manually controlled using the keyboard while SLAM Toolbox continuously updated the occupancy grid map.

키보드를 이용하여 Robot을 이동시키면서 Occupancy Grid Map을 생성하였다.

```bash
ros2 run turtlebot3_teleop teleop_keyboard
```

As LaserScan data accumulated, the generated map gradually expanded.

LaserScan 데이터가 누적될수록 Occupancy Grid가 실시간으로 갱신되는 것을 확인하였다.

---

# 6. Occupancy Grid Map

SLAM Toolbox represents the environment as an Occupancy Grid.

SLAM Toolbox는 환경을 Occupancy Grid 형태로 표현한다.

Each grid cell indicates whether the corresponding area is occupied.

| Value | Meaning |
|---------|----------|
| -1 | Unknown |
| 0 | Free Space |
| 100 | Occupied |

The generated map is published as

```
nav_msgs/msg/OccupancyGrid
```

through the `/map` topic.

생성된 지도는 `/map` Topic을 통해 `nav_msgs/msg/OccupancyGrid` 형태로 Publish된다.

---

# 7. Verifying the Published Map

The generated map was verified through the `/map` topic.

생성된 지도는 `/map` Topic을 통해 확인하였다.

```bash
ros2 topic info /map

ros2 topic echo /map --once
```

The published map contains

- resolution
- width
- height
- origin
- occupancy data

which describe the generated occupancy grid.

또한 `resolution`, `width`, `height`, `origin`, `occupancy data`를 통해 생성된 지도의 정보를 확인하였다.

---

# 8. Saving the Generated Map

After mapping was completed, the occupancy grid was saved for future navigation.

생성이 완료된 지도를 Navigation2에서 사용하기 위해 저장하였다.

```bash
ros2 run nav2_map_server map_saver_cli -f my_map
```

The following files were generated.

```
my_map.yaml

my_map.pgm
```

The YAML file stores map metadata, while the PGM file stores the occupancy grid image.

`my_map.yaml`에는 지도 정보가 저장되고, `my_map.pgm`에는 실제 Occupancy Grid 이미지가 저장된다.

---

# 9. SLAM Data Flow

```
Gazebo
     │
     ├────────► /scan
     ├────────► /odom
     ├────────► /tf
     │
     ▼
SLAM Toolbox
     │
     ├────────► Robot Pose Estimation
     ├────────► Occupancy Grid Mapping
     │
     ├────────► /map
     └────────► map → odom
     │
     ▼
RViz

↓

my_map.yaml
my_map.pgm
```

SLAM Toolbox estimates the robot pose using LaserScan and odometry while continuously generating the occupancy grid map. The saved map can later be loaded by Navigation2 for localization and autonomous navigation.

SLAM Toolbox는 LaserScan과 Odometry를 이용하여 Robot의 위치를 추정하면서 Occupancy Grid Map을 생성한다. 생성된 지도는 이후 Navigation2에서 Localization과 Autonomous Navigation에 활용된다.

---

# Key Takeaways

- SLAM simultaneously performs localization and mapping.
- SLAM Toolbox uses LaserScan, Odometry, and TF to estimate the robot pose.
- The generated map is published through the `/map` topic as an Occupancy Grid.
- The occupancy grid can be saved as `.yaml` and `.pgm` files.
- The saved map will be reused by Navigation2 for autonomous navigation.

이번 파트를 통해 SLAM Toolbox를 이용하여 Robot의 위치를 추정하면서 Occupancy Grid Map을 생성하고 저장하는 과정을 구현하였다. 또한 생성된 지도를 이후 Navigation2 기반 자율주행 시스템에서 활용할 수 있는 기반을 구축하였다.

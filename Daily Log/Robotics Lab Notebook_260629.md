# 04. Multi-Robot Spawn, Namespace & Launch Files (Part 2)

## Objective

Understand how to manually spawn multiple TurtleBot3 robots in Gazebo and learn the difference between Gazebo Entity and ROS2 Namespace.

Gazebo에서 여러 대의 TurtleBot3를 직접 생성하고 Gazebo Entity와 ROS2 Namespace의 차이를 이해하는 것을 목표로 한다.

---

# 1. Launch Gazebo Only

Instead of launching the entire TurtleBot3 simulation, only Gazebo was launched.

기존 TurtleBot3 전체 Launch File 대신 Gazebo만 실행하도록 변경하였다.

```python
IncludeLaunchDescription(
    PythonLaunchDescriptionSource(
        os.path.join(
            get_package_share_directory("gazebo_ros"),
            "launch",
            "gazebo.launch.py"
        )
    )
)
```

### Purpose

Separate the Gazebo environment from robot spawning.

Gazebo 환경과 Robot Spawn 과정을 분리하기 위함이다.

---

# 2. Spawn a Robot using `spawn_entity.py`

Spawned a TurtleBot3 model manually.

`spawn_entity.py`를 이용하여 TurtleBot3 모델을 직접 생성하였다.

```python
Node(
    package="gazebo_ros",
    executable="spawn_entity.py",
    arguments=[
        "-entity", "burger_1",
        "-file",
        os.path.join(
            get_package_share_directory("turtlebot3_gazebo"),
            "models",
            "turtlebot3_burger",
            "model.sdf"
        ),
        "-x", "0.0",
        "-y", "0.0",
        "-z", "0.01",
    ]
)
```

### Purpose

Spawn a TurtleBot3 model into the Gazebo world.

Gazebo 환경에 TurtleBot3 모델을 생성한다.

---

# 3. Understanding `spawn_entity.py`

`spawn_entity.py` is not the robot itself.

`spawn_entity.py`는 Robot이 아니라 Robot을 생성하는 프로그램이다.

```
Launch File
      │
      ▼
spawn_entity.py
      │
      ▼
Gazebo
      │
      ▼
model.sdf
      │
      ▼
Robot Created
```

After the robot is spawned, `spawn_entity.py` terminates.

Robot 생성이 완료되면 `spawn_entity.py`는 종료된다.

---

# 4. Important Spawn Arguments

| Argument           | Description                  |
| ------------------ | ---------------------------- |
| `-entity`          | Gazebo model name            |
| `-file`            | SDF model path               |
| `-x -y -z`         | Initial spawn position       |
| `-robot_namespace` | ROS2 namespace for the robot |

---

# 5. Spawn Multiple Robots

Added multiple `spawn_entity.py` nodes.

여러 개의 `spawn_entity.py`를 추가하여 다수의 Robot을 생성하였다.

```
Launch
│
├── Spawn burger_1
├── Spawn burger_2
└── Spawn burger_3
```

Each robot was assigned a different position.

각 Robot은 서로 다른 위치에서 생성하였다.

---

# 6. Entity vs Namespace

Initially, only different entity names were assigned.

처음에는 Entity 이름만 다르게 지정하였다.

```python
"-entity", "burger_1"
"-entity", "burger_2"
```

Although Gazebo successfully distinguished the models,

Gazebo에서는 서로 다른 모델로 인식하였지만,

ROS2 nodes still had identical names.

ROS2 Node 이름은 동일하게 생성되었다.

---

# 7. Problem Encountered

When spawning multiple robots, Gazebo crashed.

여러 Robot 생성 시 Gazebo가 비정상 종료되었다.

Error

```text
Found multiple nodes with same name:
/turtlebot3_imu
```

### Reason

Each robot created identical ROS2 node names.

모든 Robot이 동일한 ROS2 Node 이름을 생성하여 충돌이 발생하였다.

```
Robot 1

turtlebot3_imu

Robot 2

turtlebot3_imu
```

---

# 8. Solution — Robot Namespace

Assigned a unique namespace to every robot.

각 Robot에 서로 다른 Namespace를 지정하였다.

```python
"-robot_namespace", "tb3_0"
```

```python
"-robot_namespace", "tb3_1"
```

```python
"-robot_namespace", "tb3_2"
```

---

# 9. Result

Each robot now publishes independent ROS2 topics.

각 Robot은 독립적인 ROS2 Topic을 생성하였다.

```
/tb3_0/scan
/tb3_0/odom
/tb3_0/cmd_vel

/tb3_1/scan
/tb3_1/odom
/tb3_1/cmd_vel

/tb3_2/scan
/tb3_2/odom
/tb3_2/cmd_vel
```

Node name collisions disappeared.

Node 이름 충돌이 해결되었으며 Gazebo도 정상 동작하였다.

---

# 10. Entity vs Robot Namespace

## Entity

```
-entity burger_1
```

Used only inside Gazebo.

Gazebo에서 모델을 구분하기 위한 이름이다.

```
World

burger_1
burger_2
burger_3
```

---

## Robot Namespace

```
-robot_namespace tb3_0
```

Used by ROS2.

ROS2 Node와 Topic을 구분하기 위한 Namespace이다.

```
/tb3_0/scan
/tb3_0/odom
/tb3_0/cmd_vel
```

---

# 11. Important Discovery

The following are different.

다음 두 개념은 서로 다르다.

```python
Node(
    namespace="tb3_0"
)
```

This changes only the namespace of `spawn_entity.py`.

`spawn_entity.py` 자체의 Namespace만 변경한다.

---

```python
"-robot_namespace", "tb3_0"
```

This passes the namespace to the Gazebo plugins inside the robot model.

Robot 내부 Gazebo Plugin에게 Namespace를 전달하여 생성되는 모든 ROS2 Node와 Topic에 적용된다.

---

# Final Launch Flow

```
LaunchDescription
│
├── Include Gazebo
│
├── Spawn Robot 1
│      ├── Entity : burger_1
│      └── Namespace : tb3_0
│
├── Spawn Robot 2
│      ├── Entity : burger_2
│      └── Namespace : tb3_1
│
└── Spawn Robot 3
       ├── Entity : burger_3
       └── Namespace : tb3_2
```

---

# Key Concepts Learned

* `spawn_entity.py` creates a robot in Gazebo.
* A Launch File can spawn multiple robots by creating multiple `Node()` actions.
* `Entity` identifies robots inside Gazebo.
* `Robot Namespace` separates ROS2 nodes and topics.
* `Node(namespace=...)` and `-robot_namespace` have different purposes.
* Multiple robots require unique namespaces to avoid ROS2 node collisions.

---

# Commands Used

```bash
colcon build
```

```bash
source install/setup.bash
```

```bash
ros2 launch multi_robot_bringup gazebo.launch.py
```

```bash
ros2 topic list
```

```bash
ros2 node list
```

---

# Questions & Notes

### Why is `-robot_namespace` required?

Gazebo Entity names are only used to distinguish models inside Gazebo. ROS2 Nodes and Topics require independent namespaces to avoid name collisions when multiple robots are spawned.

Gazebo의 Entity는 모델만 구분하며 ROS2 Node와 Topic은 구분하지 않는다. 따라서 여러 Robot을 동시에 사용할 경우 `-robot_namespace`를 통해 각 Robot의 ROS2 Namespace를 분리해야 한다.

---

# Troubleshooting

## Gazebo launched but `spawn_entity.py` did not work

During development, Gazebo occasionally behaved unexpectedly because old ROS2/Gazebo processes were still running.

개발 중 이전 Gazebo 또는 `spawn_entity.py` 프로세스가 종료되지 않아 Launch File이 정상적으로 동작하지 않는 문제가 발생하였다.

### Symptoms

- Gazebo crashed unexpectedly.
- `spawn_entity.py` waited forever for `/spawn_entity`.
- Newly modified Launch Files appeared to have no effect.
- Previously spawned robots caused unexpected behavior.

### Solution

Terminate remaining Gazebo and ROS2 processes before relaunching.

실행 중인 Gazebo 및 `spawn_entity.py` 프로세스를 종료한 후 다시 실행하였다.

```bash
killall gzserver gzclient
```

```bash
pkill -f spawn_entity.py
```

If necessary,

필요한 경우

```bash
pkill -f ros2
```

can also terminate all remaining ROS2 processes.

### Why?

`spawn_entity.py` is a temporary process used to insert a robot into Gazebo.

However, if the launch process is interrupted or Gazebo crashes, some processes may remain alive and interfere with subsequent launches.

`spawn_entity.py`는 Robot을 생성하는 일시적인 프로그램이지만, Launch가 비정상 종료되면 프로세스가 남아 다음 실행과 충돌할 수 있다.

### Lesson Learned

When ROS2 or Gazebo behaves unexpectedly,

ROS2 또는 Gazebo가 예상과 다르게 동작하면 먼저 실행 중인 프로세스를 정리하는 것이 좋은 디버깅 습관이다.

```bash
killall gzserver gzclient
pkill -f spawn_entity.py
source install/setup.bash
```

# 06. Launch Arguments, OpaqueFunction & Runtime Robot Generation

## Objective

Learn how to pass runtime arguments into a ROS2 Launch File and generate an arbitrary number of robots without modifying the source code.

ROS2 Launch Argument와 OpaqueFunction을 이용하여 Launch 실행 시 Robot 개수를 동적으로 변경하는 방법을 학습한다.

---

# 1. Motivation

Previously, the number of robots was fixed.

기존에는 Robot 개수를 코드에서 직접 수정해야 했다.

```python
NUM_ROBOTS = 3
```

To create 5 robots, the source code had to be modified.

Robot 개수를 변경하려면 Launch File을 수정해야 했다.

---

# 2. DeclareLaunchArgument

Added a launch argument.

Launch Argument를 추가하였다.

```python
DeclareLaunchArgument(
    "num_robots",
    default_value="3"
)
```

Now the launch file can receive user input.

이제 Launch 실행 시 값을 전달할 수 있다.

```bash
ros2 launch multi_robot_bringup gazebo.launch.py num_robots:=5
```

---

# 3. LaunchConfiguration

Retrieved the launch argument.

Launch Argument 값을 참조하기 위해 LaunchConfiguration을 사용하였다.

```python
num_robots = LaunchConfiguration("num_robots")
```

---

# 4. Why LaunchConfiguration Cannot Be Used Directly

Attempting

```python
for i in range(num_robots):
```

generated the following error.

```text
TypeError:
'LaunchConfiguration' object cannot be interpreted as an integer
```

### Reason

`LaunchConfiguration` is **not** an integer.

It is a placeholder whose value is resolved only when the Launch System is executed.

LaunchConfiguration은 실제 값이 아니라 Launch 실행 시 결정되는 Placeholder이다.

---

# 5. OpaqueFunction

To obtain the actual value, `OpaqueFunction` was introduced.

Launch 실행 이후 실제 값을 사용하기 위해 OpaqueFunction을 사용하였다.

```python
OpaqueFunction(
    function=spawn_robots
)
```
### What is OpaqueFunction?

`OpaqueFunction` executes a Python function **after** the ROS2 Launch System has resolved all Launch Arguments.

OpaqueFunction은 Launch System이 Launch Argument를 모두 해석한 이후 Python 함수를 실행하는 Action이다.

Without `OpaqueFunction`

```python
num_robots = LaunchConfiguration("num_robots")

range(num_robots)    ❌
```

`LaunchConfiguration` is only a placeholder, not an actual integer.

LaunchConfiguration은 실제 값이 아니라 Placeholder 객체이다.

With `OpaqueFunction`

```python
def spawn_robots(context):

    num_robots = int(
        LaunchConfiguration("num_robots").perform(context)
    )
```

The runtime value can now be converted into a normal Python integer and used by the program.

Launch 실행 시 실제 값을 Python의 int로 변환하여 사용할 수 있다.


---

# 6. Accessing Runtime Values

Inside `OpaqueFunction`, the launch argument can be converted into an integer.

OpaqueFunction 내부에서는 Launch Argument를 실제 값으로 변환할 수 있다.

```python
num_robots = int(
    LaunchConfiguration("num_robots").perform(context)
)
```

### Purpose

Convert the runtime launch argument into a Python integer.

Launch Argument를 Python의 int 타입으로 변환한다.

---

# 7. Runtime Robot Generation

Robot generation was moved into `spawn_robots()`.

Robot 생성 로직을 별도의 함수로 분리하였다.

```python
for i in range(num_robots):
    actions.append(
        spawn_robot(...)
    )
```

The function returns a list of `Node` objects.

`spawn_robots()`는 여러 개의 Node를 생성하여 반환한다.

---

# 8. Final Launch Flow

```
DeclareLaunchArgument
        │
        ▼
LaunchConfiguration
        │
        ▼
OpaqueFunction
        │
        ▼
perform(context)
        │
        ▼
Python int
        │
        ▼
spawn_robot()
        │
        ▼
Node
        │
        ▼
Gazebo
```

---

# 9. Verification

Default

```bash
ros2 launch multi_robot_bringup gazebo.launch.py
```

Output

```
3 robots
```

Runtime argument

```bash
ros2 launch multi_robot_bringup gazebo.launch.py num_robots:=5
```

Output

```
5 robots
```

Robot generation was successfully controlled without modifying the source code.

Launch File 수정 없이 Robot 개수를 변경할 수 있음을 확인하였다.

---

# 10. Introduction to robot_state_publisher

Attempted to execute

```bash
ros2 run robot_state_publisher robot_state_publisher
```

Result

```text
[FATAL]
robot_description parameter must not be empty
```

### Observation

`robot_state_publisher` requires a robot model (`robot_description`) before it can publish TF.

robot_state_publisher는 TF를 생성하기 위해 robot_description(URDF)이 반드시 필요하다.

---

# 11. Exploring TurtleBot3 URDF

Checked the TurtleBot3 URDF.

```bash
ls /opt/ros/humble/share/turtlebot3_description/urdf
```

```
turtlebot3_burger.urdf
```

Examined the file.

```bash
head -20 turtlebot3_burger.urdf
```

Found

```xml
<xacro:arg name="namespace" default=""/>
```

The TurtleBot3 model is designed to receive a namespace.

TurtleBot3 URDF는 Namespace를 전달받을 수 있도록 설계되어 있다.

---

# 12. Xacro to URDF

Converted the Xacro-based URDF into a pure URDF.

```bash
xacro turtlebot3_burger.urdf
```

Verified that Xacro expands into a standard URDF before being used by `robot_state_publisher`.

Xacro는 robot_state_publisher가 사용하기 전에 일반 URDF로 변환된다.

---

# Key Concepts Learned

- DeclareLaunchArgument
- LaunchConfiguration
- OpaqueFunction
- perform(context)
- Runtime Launch Arguments
- Dynamic Robot Generation
- robot_state_publisher requires `robot_description`
- Xacro is converted into URDF before publishing TF

---

# Commands Used

```bash
ros2 run robot_state_publisher robot_state_publisher
```

```bash
ls /opt/ros/humble/share/turtlebot3_description/urdf
```

```bash
head -20 /opt/ros/humble/share/turtlebot3_description/urdf/turtlebot3_burger.urdf
```

```bash
xacro /opt/ros/humble/share/turtlebot3_description/urdf/turtlebot3_burger.urdf
```

---

# Questions & Notes

---

# Interview Quiz

## Q1. Why couldn't you use `LaunchConfiguration("num_robots")` directly inside `range()`?

### Answer

`LaunchConfiguration` does not return a Python integer.

Instead, it returns a **Launch substitution (placeholder)** whose value is resolved only when the ROS2 Launch System executes.

Since `range()` requires an integer, `LaunchConfiguration` must first be converted into an actual value using `perform(context)`.

LaunchConfiguration은 Python의 int를 반환하지 않는다.

대신 **Launch 실행 시 결정되는 Placeholder 객체**를 반환한다.

`range()`는 int 타입만 사용할 수 있으므로, `perform(context)`를 이용하여 실제 값으로 변환해야 한다.

```python
num_robots = int(
    LaunchConfiguration("num_robots").perform(context)
)
```

---

## Q2. What problem does `OpaqueFunction` solve?

### Answer

`OpaqueFunction` executes a Python function **after** the ROS2 Launch System has resolved all Launch Arguments.

This allows `LaunchConfiguration` placeholders to be converted into actual Python values.

`OpaqueFunction`은 ROS2 Launch System이 Launch Argument를 모두 해석한 이후 Python 함수를 실행하는 Action이다.

따라서 `LaunchConfiguration`이 가지고 있는 Placeholder를 실제 Python 값으로 변환하여 사용할 수 있다.

Without `OpaqueFunction`, runtime launch arguments cannot be used inside normal Python logic.

OpaqueFunction이 없다면 Launch Argument를 일반 Python 코드에서 사용할 수 없다.

---

## Q3. What is the difference between `DeclareLaunchArgument` and `LaunchConfiguration`?

### Answer

| Component | Description |
|-----------|-------------|
| `DeclareLaunchArgument` | Declares a launch argument. |
| `LaunchConfiguration` | Retrieves the value of the launch argument. |

| 구성 요소 | 설명 |
|-----------|------|
| `DeclareLaunchArgument` | Launch Argument를 선언한다. |
| `LaunchConfiguration` | 선언된 Launch Argument의 값을 가져온다. |

Example

```python
DeclareLaunchArgument(
    "num_robots",
    default_value="3"
)
```

↓

```python
LaunchConfiguration("num_robots")
```

Think of it as

```
DeclareLaunchArgument
        ↓
Variable Declaration

LaunchConfiguration
        ↓
Variable Access
```

즉,

```
DeclareLaunchArgument
        ↓
변수 선언

LaunchConfiguration
        ↓
변수 사용
```

---

## Q4. Why is `robot_state_publisher` unable to run without `robot_description`?

### Answer

`robot_state_publisher` generates the robot's TF Tree from the robot model.

Without `robot_description` (URDF), it does not know the robot's Links or Joints and therefore cannot publish TF.

`robot_state_publisher`는 Robot Model(URDF)을 읽어 TF Tree를 생성한다.

URDF가 없으면 Robot의 Link와 Joint 정보를 알 수 없으므로 TF를 생성할 수 없다.

Flow

```
URDF
    │
    ▼
robot_state_publisher
    │
    ▼
TF Tree
```

---

## Q5. Why does ROS2 use Xacro before passing the robot model to `robot_state_publisher`?

### Answer

Xacro improves **reusability** and **maintainability**.

Instead of creating multiple large URDF files with duplicated content, common robot components can be shared using Xacro.

Xacro는 **재사용성(Reusability)** 과 **유지보수성(Maintainability)** 을 향상시키기 위해 사용된다.

공통되는 Robot Model을 하나의 Xacro 파일로 관리하고, 필요한 부분만 변경하여 여러 Robot Model을 생성할 수 있다.

Benefits

- Reduce duplicated code
- Improve maintainability
- Improve reusability
- Support multiple robot models

장점

- 코드 중복 감소
- 유지보수성 향상
- 재사용성 향상
- 여러 Robot Model 지원

Flow

```
Xacro
    │
    ▼
URDF
    │
    ▼
robot_state_publisher
    │
    ▼
TF Tree
```

---

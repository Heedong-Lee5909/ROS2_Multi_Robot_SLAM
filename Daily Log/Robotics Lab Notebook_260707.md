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

### Why is OpaqueFunction required?

`LaunchConfiguration` is not a Python variable. Its value is only available after the Launch System starts.

LaunchConfiguration는 Python 변수가 아니라 Launch 실행 시 결정되는 값이므로 OpaqueFunction 내부에서 사용해야 한다.

---

### Why can't LaunchConfiguration be used inside `range()`?

`range()` requires an integer, while `LaunchConfiguration` is only a launch substitution object.

range()는 int를 요구하지만 LaunchConfiguration은 Placeholder 객체이므로 사용할 수 없다.

---

### What is the role of robot_state_publisher?

It reads a robot model (URDF) and publishes the TF tree.

URDF를 읽어 TF Tree를 생성하는 역할을 수행한다.

---

### What is the relationship between Xacro and URDF?

Xacro is converted into a standard URDF before being consumed by `robot_state_publisher`.

robot_state_publisher는 Xacro가 아닌 변환된 URDF를 입력으로 사용한다.

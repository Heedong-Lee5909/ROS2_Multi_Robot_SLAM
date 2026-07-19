# 03. Multi-Robot Spawn, Namespace & Launch Files (Part 1)

## Objective

Understand the basic structure of ROS2 Launch Files by creating a custom launch file that executes an existing TurtleBot3 Gazebo simulation.

기존 TurtleBot3 Gazebo 시뮬레이션을 직접 실행하는 Launch File을 작성하며 ROS2 Launch File의 기본 구조와 동작 원리를 이해하는 것을 목표로 한다.

---

# 1. Create a Custom Launch File

Created a new package named `multi_robot_bringup` and added a custom launch file.

`multi_robot_bringup` 패키지를 생성하고 사용자 정의 Launch File을 작성하였다.

### Project Structure

```text
multi_robot_ws/
└── src/
    └── multi_robot_bringup/
        ├── launch/
        │   └── gazebo.launch.py
        ├── package.xml
        └── setup.py
```

---

# 2. Basic Structure of a Launch File

Implemented the minimum structure required for a ROS2 Launch File.

ROS2 Launch File의 최소 구조를 구현하였다.

```python
from launch import LaunchDescription

def generate_launch_description():
    return LaunchDescription([
    ])
```

### Purpose

`LaunchDescription()` defines a list of actions that will be executed when the launch file is started.

`LaunchDescription()`는 Launch File 실행 시 수행할 Action들의 목록을 정의한다.

---

# 3. Include an Existing Launch File

Included the existing TurtleBot3 Gazebo launch file inside the custom launch file.

기존 TurtleBot3 Gazebo Launch File을 사용자 Launch File 내부에서 실행하도록 구성하였다.

```python
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

from ament_index_python.packages import get_package_share_directory

import os
```

```python
IncludeLaunchDescription(
    PythonLaunchDescriptionSource(
        os.path.join(
            get_package_share_directory("turtlebot3_gazebo"),
            "launch",
            "turtlebot3_world.launch.py"
        )
    )
)
```

### Purpose

Execute an existing Launch File from another Launch File.

다른 Launch File 내부에서 기존 Launch File을 실행한다.

---

# 4. Understanding Each Component

| Component                       | Description                                                        |
| ------------------------------- | ------------------------------------------------------------------ |
| `LaunchDescription`             | Defines actions to execute (실행할 Action 목록 정의)                      |
| `IncludeLaunchDescription`      | Executes another Launch File (다른 Launch File 실행)                   |
| `PythonLaunchDescriptionSource` | Specifies which Python Launch File to execute (실행할 Launch File 지정) |
| `get_package_share_directory()` | Finds the package's share directory (패키지의 share 디렉터리 검색)           |
| `os.path.join()`                | Creates a platform-independent file path (운영체제와 관계없이 경로 생성)        |

---

# 5. Why Use `get_package_share_directory()`?

Instead of hardcoding installation paths, ROS2 automatically locates the package directory.

설치 경로를 직접 입력하지 않고 ROS2가 패키지 설치 위치를 자동으로 찾아준다.

Example

```python
get_package_share_directory("turtlebot3_gazebo")
```

↓

```text
/opt/ros/humble/share/turtlebot3_gazebo
```

### Advantages

* Independent of ROS2 distribution (Humble, Iron, Jazzy, etc.)

* No hardcoded absolute paths

* Improves portability

* ROS2 버전에 독립적

* 절대 경로 사용 불필요

* 이식성 향상

---

# 6. Installing Launch Files

Initially, ROS2 could not find the custom launch file.

처음에는 ROS2가 작성한 Launch File을 찾지 못하였다.

### Error

```text
file 'gazebo.launch.py' was not found
```

### Reason

ROS2 executes launch files from the **install** directory, not from the **src** directory.

ROS2는 **src** 폴더가 아닌 **install** 폴더의 Launch File을 실행한다.

### Solution

Added the following entry to `setup.py`.

`setup.py`에 Launch 폴더를 설치 대상으로 등록하였다.

```python
from glob import glob
```

```python
data_files=[
    ('share/ament_index/resource_index/packages',
        ['resource/' + package_name]),
    ('share/' + package_name, ['package.xml']),
    ('share/' + package_name + '/launch',
        glob('launch/*.launch.py')),
]
```

### Purpose

Copy all launch files into the install directory during `colcon build`.

`colcon build` 시 모든 Launch File을 install 디렉터리로 복사한다.

---

# 7. Build Process

After modifying `setup.py`, rebuilt the workspace.

`setup.py` 수정 후 Workspace를 다시 빌드하였다.

```bash
colcon build
```

```bash
source install/setup.bash
```

Verified that

```text
install/
└── multi_robot_bringup/
    └── share/
        └── multi_robot_bringup/
            └── launch/
                └── gazebo.launch.py
```

was successfully created.

---

# 8. Execute the Custom Launch File

Successfully launched Gazebo using the custom launch file.

사용자 정의 Launch File을 이용하여 Gazebo를 정상 실행하였다.

```bash
ros2 launch multi_robot_bringup gazebo.launch.py
```

The custom launch file successfully included and executed the original `turtlebot3_world.launch.py`.

작성한 Launch File이 기존 `turtlebot3_world.launch.py`를 정상적으로 포함하여 실행하는 것을 확인하였다.

---

# Key Concepts Learned

* ROS2 executes Launch Files from the **install** directory, not the **src** directory.
* `LaunchDescription` stores executable actions.
* `IncludeLaunchDescription` executes another Launch File.
* `PythonLaunchDescriptionSource` specifies which Launch File to execute.
* `get_package_share_directory()` locates the package installation path.
* `glob()` automatically installs all launch files.
* Custom Launch Files can reuse existing Launch Files using `IncludeLaunchDescription`.

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
tree install/multi_robot_bringup/share/multi_robot_bringup
```

---

# Questions & Notes

### Why doesn't ROS2 execute Launch Files directly from `src`?

ROS2 executes installed packages to ensure consistent runtime behavior. Therefore, launch files must be copied into the `install` directory during the build process.

ROS2는 실행 시 `src`가 아닌 `install` 디렉터리의 패키지를 사용한다. 따라서 Launch File도 빌드 과정에서 `install`로 복사되어야 한다.

---

### Why use `glob('launch/*.launch.py')`?

Instead of listing every launch file manually, `glob()` automatically includes all launch files in the `launch` directory.

각 Launch File을 직접 등록하지 않고 `launch` 폴더 내의 모든 `.launch.py` 파일을 자동으로 설치하기 위해 사용한다.

---


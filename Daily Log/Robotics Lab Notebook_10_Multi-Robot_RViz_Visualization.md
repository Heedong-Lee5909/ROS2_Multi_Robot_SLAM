# Part 3. Building a Dynamic Multi-Robot Launch System

## Objective

In the previous sections, each TurtleBot3 was successfully visualized in RViz.

However, the launch file still required several manual configurations, including static TF creation, SDF modification, and robot spawning.

In this section, the launch system is redesigned to automatically generate all required resources for an arbitrary number of robots.

앞선 파트에서는 각 TurtleBot3를 RViz에서 정상적으로 시각화하였다.

하지만 Launch 파일에는 Static TF 생성, SDF 수정, Robot Spawn과 같은 작업이 수동으로 이루어지고 있었다.

이번 파트에서는 이러한 과정을 자동화하여 원하는 개수의 Robot을 동적으로 생성할 수 있는 Multi-Robot Launch System을 구축한다.

---

# 1. Creating Static World Transforms

Although each robot published its own TF Tree, all robots still required a common parent frame.

각 Robot은 독립적인 TF Tree를 생성하지만, 모든 Robot을 하나의 좌표계에서 표현하기 위해서는 공통 부모 Frame이 필요하다.

To automate this process, a helper function named `static_tf_node()` was implemented.

이를 자동화하기 위해 `static_tf_node()` 함수를 구현하였다.

```python
def static_tf_node(namespace):
    return Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        ...
    )
```

This function automatically creates

```
world
    │
    ▼
tb3_x/odom
```

for every robot.

이를 통해 모든 Robot이 하나의 World Frame 아래에 연결되도록 구성하였다.

---

# 2. Dynamically Generating SDF Files

The default TurtleBot3 SDF model contains fixed frame names.

기본 TurtleBot3 SDF는 모든 Frame 이름이 고정되어 있다.

For a multi-robot simulation, each robot requires unique frame names.

하지만 Multi-Robot 환경에서는 모든 Robot이 서로 다른 Frame 이름을 가져야 한다.

To solve this problem, the `generate_sdf()` function was implemented.

이를 해결하기 위해 `generate_sdf()` 함수를 작성하였다.

```python
def generate_sdf(namespace):
```

Instead of manually preparing multiple SDF files, the original model is modified at runtime.

여러 개의 SDF 파일을 미리 준비하는 대신, Launch 시점에 SDF를 동적으로 수정하도록 구현하였다.

The following fields are updated automatically.

- `odometry_frame`
- `robot_base_frame`
- `frame_name`

Each frame is prefixed with the robot namespace.

각 Frame에는 Robot Namespace가 자동으로 추가된다.

---

# 3. Updating Sensor Frames

One of the modified fields is

```xml
<frame_name>
```

This field determines the `frame_id` of LaserScan messages.

`frame_name`은 Gazebo가 Publish하는 LaserScan Message의 `frame_id`를 결정한다.

The original model contained

```xml
<frame_name>base_scan</frame_name>
```

which caused a mismatch with the TF Tree.

기본 SDF에서는 `base_scan`을 사용하고 있었기 때문에 TF Tree와 이름이 일치하지 않았다.

The frame name was updated dynamically.

```python
content = content.replace(
    "<frame_name>base_scan</frame_name>",
    f"<frame_name>{namespace}/base_scan</frame_name>"
)
```

After this modification, the published LaserScan messages matched the TF Tree correctly.

수정 이후 LaserScan Message의 `frame_id`와 TF Frame이 일치하게 되었다.

---

# 4. Automating Robot Spawning

A reusable `spawn_robot()` function was implemented.

Robot 생성 과정을 자동화하기 위해 `spawn_robot()` 함수를 구현하였다.

Each robot receives

- robot name
- namespace
- spawn position

as arguments.

Robot 이름, Namespace, Spawn 위치를 인자로 받아 원하는 Robot을 생성하도록 구성하였다.

---

# 5. Publishing Robot States

Each robot also requires its own `robot_state_publisher`.

각 Robot은 독립적인 `robot_state_publisher`를 실행해야 한다.

The following parameter was added.

```python
frame_prefix
```

As a result, every TF frame became

```
tb3_0/base_link

tb3_1/base_link

tb3_2/base_link
```

instead of sharing identical frame names.

모든 Robot이 서로 다른 TF Frame을 갖도록 구성하였다.

---

# 6. Dynamic Robot Creation using OpaqueFunction

Finally, every robot is generated inside

```python
spawn_robots()
```

using

```python
OpaqueFunction(function=spawn_robots)
```

The number of robots is obtained from

```python
num_robots
```

and all required nodes are generated automatically.

Launch Argument에 따라 Robot 개수만 변경하면 필요한 모든 Node가 자동으로 생성된다.

---

# 7. Final Launch Architecture

```
Launch File
        │
        ▼
OpaqueFunction
        │
        ▼
spawn_robots()
        │
        ├──────────────┐
        ▼              ▼
spawn_entity     robot_state_publisher
        │              │
        ▼              ▼
generate_sdf()        TF
        │              │
        ▼              │
Gazebo Model           │
        │              │
        ├──────────────┘
        ▼
static_transform_publisher
        │
        ▼
RViz
```

---

# Key Takeaways

- Static TFs are generated automatically.
- SDF files are modified dynamically.
- Sensor frames are updated automatically.
- Robot spawning is fully automated.
- The launch system scales to an arbitrary number of robots.
- Only the `num_robots` argument needs to be changed to create additional robots.

이번 파트를 통해 Multi-Robot Launch 시스템을 모듈화하고 자동화하여, Robot 수가 증가하더라도 동일한 Launch 파일을 재사용할 수 있는 구조를 구축하였다.

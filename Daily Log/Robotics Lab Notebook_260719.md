# 08. Multi-Robot RViz Visualization (Part 1)

## Objective

In this chapter, we visualize multiple TurtleBot3 robots in RViz and understand how RViz uses TF, URDF, and sensor data to display robot states.

Unlike Gazebo, which focuses on physics simulation, RViz provides a convenient way to inspect the internal state of a robot, including its coordinate frames, robot model, and sensor outputs.

이번 장에서는 RViz를 이용하여 여러 대의 TurtleBot3를 시각화하고, RViz가 TF, URDF, 그리고 Sensor 데이터를 이용하여 Robot을 표현하는 원리를 학습한다.

Gazebo가 물리 시뮬레이션을 수행하는 도구라면, RViz는 Robot의 내부 상태를 확인하고 디버깅하기 위한 시각화 도구이다.

---

# 1. Why do we need RViz?

Until now, all robots have been executed successfully in Gazebo.

지금까지는 Gazebo에서 여러 Robot을 성공적으로 실행하였다.

Gazebo allows us to verify that robots move correctly and interact with the simulated environment.

Gazebo에서는 Robot이 정상적으로 움직이고 환경과 상호작용하는지를 확인할 수 있다.

However, Gazebo provides very limited information about the robot's internal state.

하지만 Gazebo만으로는 Robot 내부 상태를 확인하기 어렵다.

For example, it is impossible to determine

- whether TF is published correctly,
- whether the URDF is loaded,
- whether LaserScan messages are received,
- or whether coordinate frames are connected properly.

예를 들어 Gazebo에서는 TF가 제대로 생성되었는지, URDF가 정상적으로 로드되었는지, LaserScan이 Publish되고 있는지 등을 확인하기 어렵다.

For debugging a ROS2 robot, RViz is therefore an essential tool.

따라서 ROS2 Robot을 개발할 때 RViz는 필수적인 디버깅 도구이다.

RViz visualizes ROS topics such as

- RobotModel
- TF
- LaserScan
- PointCloud
- Occupancy Grid Map
- Navigation Path

instead of performing physics simulation.

RViz는 물리 시뮬레이션을 수행하는 것이 아니라 ROS Topic을 시각화하는 역할을 수행한다.

---

# 2. Launching RViz

RViz was launched using

```bash
rviz2
```

The RViz window opened successfully.

RViz가 정상적으로 실행되는 것을 확인하였다.

However, the Global Status immediately displayed the following warning.

```
No TF data.
Actual error:
Fixed Frame [map] does not exist.
```

At first glance, this looked like a TF publishing problem.

처음에는 TF가 제대로 Publish되지 않는 문제처럼 보였다.

However, the actual reason was different.

하지만 실제 원인은 TF가 존재하지 않는 것이 아니었다.

---

# 3. Why did "No TF data" appear?

Each TurtleBot already published its own TF Tree.

각 Robot은 이미 자신의 TF Tree를 Publish하고 있었다.

For example,

```
tb3_0/odom
    │
    ├── base_footprint
    │
    ├── base_link
    │
    ├── base_scan
    │
    └── imu_link
```

was successfully generated.

The same TF Tree also existed for

```
tb3_1

tb3_2
```

Therefore, the TF system itself was working correctly.

즉, TF 자체에는 문제가 없었다.

The real problem was that RViz uses one coordinate frame as the reference for every visualization.

실제 문제는 RViz가 하나의 기준 좌표계를 필요로 한다는 점이었다.

This coordinate frame is called the **Fixed Frame**.

이 기준 좌표계를 Fixed Frame이라고 한다.

By default, RViz uses

```
map
```

as its Fixed Frame.

하지만 현재 프로젝트에서는 SLAM을 실행하지 않았기 때문에 `map` Frame이 존재하지 않았다.

As a result, RViz failed to find the Fixed Frame and displayed the warning message.

결국 RViz는 기준 좌표계를 찾지 못하여 "No TF data" 오류를 출력한 것이다.

---

# 4. Why is a Fixed Frame necessary?

RViz visualizes every object with respect to one reference coordinate system.

RViz는 모든 데이터를 하나의 기준 좌표계를 기준으로 표시한다.

For a single robot,

```
odom
```

can simply be selected as the Fixed Frame.

단일 Robot에서는 보통 `odom`을 Fixed Frame으로 선택하면 된다.

However, this project contains three independent robots.

하지만 이번 프로젝트에는 세 대의 Robot이 존재한다.

Each robot owns its own TF Tree.

```
tb3_0/odom

tb3_1/odom

tb3_2/odom
```

These frames are completely independent.

각 Robot의 TF Tree는 서로 연결되어 있지 않다.

Therefore, RViz cannot determine the relative positions of multiple robots using only these frames.

즉, RViz는 여러 Robot을 하나의 좌표계에서 동시에 표현할 수 없다.

A common parent frame is therefore required.

따라서 모든 Robot을 연결하는 공통 부모 좌표계가 필요하다.

---

# 5. Creating a World Frame

To solve this problem, a static transform was created between the `world` frame and each robot's `odom` frame.

이를 해결하기 위해 `world`와 각 Robot의 `odom` 사이에 Static Transform을 생성하였다.

```python
def static_tf_node(namespace):
    return Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name=f"{namespace}_world_tf",
        arguments=[
            "0","0","0",
            "0","0","0",
            "world",
            f"{namespace}/odom",
        ],
    )
```

`static_transform_publisher` continuously publishes a fixed transform between two coordinate frames.

`static_transform_publisher`는 두 좌표계 사이의 고정된 Transform을 지속적으로 Publish하는 ROS2 Node이다.

Since every robot starts with its own `odom` frame, this node connects all robots to the same global frame.

각 Robot은 독립적인 `odom` Frame에서 시작하므로, 해당 Node를 이용하여 모든 Robot을 하나의 World Frame 아래에 연결하였다.

The final TF hierarchy became

```
world
│
├── tb3_0/odom
│
├── tb3_1/odom
│
└── tb3_2/odom
```

Now every robot shares the same global reference frame.

이제 모든 Robot이 동일한 기준 좌표계를 공유하게 되었다.

After restarting the launch file, the Fixed Frame in RViz was changed from `map` to `world`.

Launch를 다시 실행한 후 RViz의 Fixed Frame을 `world`로 변경하였다.

The "No TF data" warning disappeared, confirming that the TF Trees were successfully connected.

그 결과 "No TF data" 오류가 사라졌으며, 모든 Robot의 TF Tree가 하나의 World Frame 아래에 연결된 것을 확인하였다.

# Part 2. Visualizing Robot Models and TF in RViz

## Objective

After establishing a common World Frame, the next step is to visualize each TurtleBot3 in RViz.

In this section, we configure the RobotModel display, verify the `robot_description` topic, understand the role of `frame_prefix`, and visualize the complete TF Tree.

World Frame를 구성한 이후에는 각 Robot을 RViz에서 정상적으로 시각화해야 한다.

이번 파트에서는 RobotModel Display를 설정하고, `robot_description` Topic을 확인하며, `frame_prefix`의 역할을 이해하고, 최종적으로 TF Tree를 시각화한다.

---

# 1. Adding RobotModel

To visualize the robot, a **RobotModel** display was added in RViz.

Robot을 시각화하기 위해 RViz의 **RobotModel** Display를 추가하였다.

Immediately after adding the display, the following error appeared.

```
Status

Error
```

This indicated that RViz could not construct the robot model correctly.

RobotModel을 구성하기 위한 정보가 부족하다는 의미이다.

RobotModel requires two pieces of information.

- URDF (`robot_description`)
- TF

Both must be available before the robot can be displayed.

RobotModel은 `robot_description`과 TF 정보를 모두 필요로 하며, 둘 중 하나라도 없으면 Robot을 표시할 수 없다.

---

# 2. Verifying robot_description

The first step was to verify whether each robot was publishing its URDF.

먼저 각 Robot이 자신의 URDF를 Publish하고 있는지 확인하였다.

```bash
ros2 topic list | grep robot_description
```

The following topics were found.

```
/tb3_0/robot_description
/tb3_1/robot_description
/tb3_2/robot_description
```

Each TurtleBot successfully published its own `robot_description`.

각 Robot이 독립적으로 `robot_description` Topic을 Publish하고 있음을 확인하였다.

The RobotModel display was then configured to subscribe to

```
/tb3_0/robot_description
```

for the first robot.

첫 번째 Robot의 `robot_description`을 선택하여 RobotModel을 구성하였다.

However, the error still remained.

하지만 RobotModel Error는 여전히 해결되지 않았다.

---

# 3. Investigating the RobotModel Error

Since the URDF was successfully loaded, the problem had to be related to TF.

URDF는 정상적으로 전달되고 있었기 때문에 문제는 TF에 있다고 판단하였다.

The RobotModel plugin searched for

```
base_link
```

but the TF Tree actually contained

```
tb3_0/base_link
```

The reason was that every TF frame had already been modified by `frame_prefix`.

`frame_prefix`가 적용되면서 모든 TF Frame 이름이 Namespace를 포함하도록 변경되었기 때문이다.

As a result, RobotModel searched for a frame that did not exist.

결과적으로 RobotModel이 존재하지 않는 Frame을 찾고 있었던 것이다.

---

# 4. Configuring TF Prefix

To resolve this mismatch, the **TF Prefix** option of RobotModel was configured.

Frame 이름 불일치를 해결하기 위해 RobotModel의 **TF Prefix**를 설정하였다.

```
TF Prefix

tb3_0
```

After applying the prefix, RobotModel correctly searched for

```
tb3_0/base_link
```

instead of

```
base_link
```

The robot immediately appeared in RViz.

Robot이 정상적으로 표시되는 것을 확인하였다.

The same configuration was repeated for

- tb3_1
- tb3_2

모든 Robot에 동일한 방법을 적용하였다.

---

# 5. Visualizing the TF Tree

After the RobotModel was displayed successfully, the TF display was added.

RobotModel이 정상적으로 표시된 이후 TF Display를 추가하였다.

```
Displays

→ Add

→ TF
```

RViz visualized every coordinate frame published by `robot_state_publisher`.

RViz가 `robot_state_publisher`에서 Publish하는 모든 좌표계를 시각화하였다.

The TF Tree for each robot included

```
tb3_0/odom
tb3_0/base_footprint
tb3_0/base_link
tb3_0/base_scan
tb3_0/imu_link
```

The same structure was also observed for

- tb3_1
- tb3_2

This confirmed that every robot had its own independent TF Tree.

각 Robot이 독립적인 TF Tree를 정상적으로 생성하고 있음을 확인하였다.

---

# Summary

In this section,

- `robot_description` was verified.
- RobotModel was configured.
- `frame_prefix` was applied through TF Prefix.
- The complete TF Tree was successfully visualized.

이를 통해 각 Robot의 URDF와 TF가 정상적으로 연결되어 RobotModel이 올바르게 시각화되는 것을 확인하였다.

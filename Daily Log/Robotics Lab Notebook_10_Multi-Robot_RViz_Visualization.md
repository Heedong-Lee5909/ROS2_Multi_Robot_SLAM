# Part 3. Debugging LaserScan Visualization

## Objective

After successfully visualizing the RobotModel and TF Tree, the final step was to display the LaserScan data in RViz.

Although the LaserScan topic was published correctly, the scan was not visualized. In this section, the cause of the problem is investigated and resolved by modifying the Gazebo sensor configuration.

RobotModel과 TF Tree를 성공적으로 시각화한 이후, 마지막으로 LaserScan 데이터를 RViz에 표시하였다.

LaserScan Topic은 정상적으로 Publish되고 있었지만 RViz에는 표시되지 않았다. 이번 파트에서는 문제의 원인을 분석하고 Gazebo Sensor 설정을 수정하여 이를 해결한다.

---

# 1. Adding the LaserScan Display

To visualize LiDAR data, a **LaserScan** display was added in RViz.

LiDAR 데이터를 시각화하기 위해 RViz에서 **LaserScan** Display를 추가하였다.

The Topic was configured as

```
/tb3_0/scan
```

However, no scan data appeared in the RViz window.

Topic은 정상적으로 선택되었지만 화면에는 아무것도 표시되지 않았다.

Since no warning was shown in RViz, the problem required further investigation.

RViz에서도 명확한 오류가 나타나지 않았기 때문에 원인을 직접 확인하기로 하였다.

---

# 2. Verifying the LaserScan Topic

The first step was to verify whether the LiDAR sensor was actually publishing data.

먼저 LiDAR 센서가 정상적으로 데이터를 Publish하고 있는지 확인하였다.

```bash
ros2 topic echo /tb3_0/scan --once
```

The following message was received.

```yaml
header:
  frame_id: base_scan

ranges:
- inf
- inf
- 2.84
- 2.76
...
```

The message confirmed that the LiDAR sensor was operating correctly.

LiDAR Sensor 자체는 정상적으로 동작하고 있음을 확인하였다.

Since the topic was being published correctly, the problem was not related to the sensor.

즉, 문제는 Sensor가 아니라 RViz가 데이터를 변환하는 과정에 있다고 판단하였다.

---

# 3. Investigating the frame_id

The next step was to compare the LaserScan frame with the TF Tree.

다음으로 LaserScan의 Frame과 TF Tree를 비교하였다.

The LaserScan message contained

```
frame_id

base_scan
```

However, the TF Tree contained

```
tb3_0/base_scan
```

The frame names did not match.

LaserScan Message의 Frame 이름과 TF Tree의 Frame 이름이 서로 달랐다.

RViz transforms every sensor message using TF.

RViz는 모든 Sensor 데이터를 TF를 이용하여 좌표 변환한 후 화면에 표시한다.

Since the frame

```
base_scan
```

did not exist in the TF Tree,

RViz could not transform the LaserScan data.

`base_scan`이라는 Frame은 존재하지 않았기 때문에 RViz가 좌표 변환을 수행하지 못했고, 결국 LaserScan이 표시되지 않았다.

The root cause was therefore identified as a frame mismatch.

결국 문제의 원인은 Frame 이름 불일치였다.

---

# 4. Updating generate_sdf()

The Gazebo Ray Sensor publishes its frame name from the SDF model.

Gazebo Ray Sensor는 SDF 파일에 정의된 Frame 이름을 그대로 사용하여 데이터를 Publish한다.

The original SDF contained

```xml
<frame_name>base_scan</frame_name>
```

Since every robot used a namespace, the frame name also needed to include the namespace.

모든 Robot이 Namespace를 사용하므로 Sensor의 Frame 이름 역시 Namespace를 포함하도록 수정해야 했다.

The following code was added to `generate_sdf()`.

```python
content = content.replace(
    "<frame_name>base_scan</frame_name>",
    f"<frame_name>{namespace}/base_scan</frame_name>"
)
```

After this modification, the Gazebo plugin published

```
tb3_0/base_scan
```

instead of

```
base_scan
```

As a result, the LaserScan frame became identical to the TF frame.

그 결과 LaserScan의 Frame 이름과 TF Tree의 Frame 이름이 서로 일치하게 되었다.

---

# 5. Verifying the Result

After rebuilding the workspace and restarting Gazebo,

```bash
colcon build

source install/setup.bash

ros2 launch ...
```

RViz immediately displayed the LaserScan data.

Workspace를 다시 Build하고 Gazebo를 재실행한 이후 LaserScan이 정상적으로 표시되는 것을 확인하였다.

The same modification was automatically applied to

- tb3_0
- tb3_1
- tb3_2

because `generate_sdf()` generates the SDF file dynamically for every robot.

`generate_sdf()`가 각 Robot의 SDF를 동적으로 생성하기 때문에 모든 Robot에 동일한 수정 사항이 적용되었다.

The final visualization correctly displayed

- RobotModel
- TF Tree
- LaserScan

for every TurtleBot3.

최종적으로 모든 TurtleBot3의 RobotModel, TF Tree, 그리고 LaserScan이 정상적으로 시각화되는 것을 확인하였다.

---

# System Architecture

```
                 Gazebo
                    │
                    ▼
          Ray Sensor Plugin
                    │
                    ▼
            /tb3_x/scan
      frame_id = tb3_x/base_scan
                    │
                    ▼
                  TF Tree
                    │
                    ▼
                 RobotModel
                    │
                    ▼
                  RViz2
```

The Gazebo Ray Sensor publishes LaserScan messages with the correct frame name.

RViz uses TF to transform the sensor data into the global coordinate system before visualization.

Gazebo Ray Sensor는 올바른 Frame 이름을 포함한 LaserScan 데이터를 Publish하며, RViz는 TF를 이용하여 이를 기준 좌표계로 변환한 후 화면에 표시한다.

---

# Questions & Notes

### Why wasn't LaserScan displayed?

The LaserScan message itself was published correctly.

However, its `frame_id` did not exist in the TF Tree.

LaserScan 데이터는 정상적으로 Publish되고 있었지만, `frame_id`가 TF Tree에 존재하지 않아 좌표 변환을 수행할 수 없었다.

---

### Why did modifying `generate_sdf()` solve the problem?

The Gazebo Ray Sensor uses the `<frame_name>` element inside the SDF model as the `frame_id` of the published LaserScan message.

By updating `<frame_name>` to include the robot namespace, the published frame became identical to the TF frame.

Gazebo Sensor Plugin은 SDF의 `<frame_name>`을 LaserScan Message의 `frame_id`로 사용한다. 따라서 Namespace를 포함하도록 수정함으로써 TF Tree와 동일한 Frame 이름을 사용하게 되었고 문제가 해결되었다.

---

### Key Takeaways

- LaserScan messages require a valid TF frame.
- The `frame_id` of a sensor message must exactly match a frame in the TF Tree.
- When using multiple robots with namespaces, sensor frames must also include the namespace.
- Dynamically modifying the SDF file in `generate_sdf()` provides an efficient solution for multi-robot simulations.

이번 실습을 통해 Sensor 데이터의 `frame_id`와 TF Tree의 Frame 이름은 반드시 일치해야 하며, Multi-Robot 환경에서는 Sensor Frame에도 Namespace를 적용해야 한다는 점을 확인하였다.

# ROS2 Multi-Robot SLAM

A ROS2-based multi-robot SLAM and autonomous exploration project using three TurtleBot3 robots in a Gazebo indoor environment.

Gazebo indoor environment에서 3대의 TurtleBot3 robot을 이용한 ROS2 기반 multi-robot SLAM 및 autonomous exploration 프로젝트이다.

The project focuses on building an independent SLAM pipeline for multiple robots, aligning their local maps in a common world coordinate frame, merging them into a global map, and enabling autonomous exploration using LiDAR-based reactive obstacle avoidance.

본 프로젝트는 multiple robot을 위한 independent SLAM pipeline을 구축하고, 각 robot의 local map을 공통 world coordinate frame에 align한 후 global map으로 merge하며, LiDAR-based reactive obstacle avoidance를 이용하여 autonomous exploration을 수행하는 것을 목표로 한다.

---

## Overview

Multi-robot systems can improve exploration efficiency by allowing multiple robots to operate simultaneously in the same environment.

Multi-robot system은 여러 robot이 동일한 environment에서 동시에 동작하도록 함으로써 exploration efficiency를 향상시킬 수 있다.

However, deploying multiple SLAM systems introduces several challenges, including:

그러나 multiple SLAM system을 동시에 운용하기 위해서는 다음과 같은 여러 challenge가 발생한다.

- Namespace isolation

- Independent TF frames

- Independent LaserScan topics

- Independent SLAM map frames

- Global map alignment

- Multi-robot map merging

- Autonomous robot coordination

This project addresses these challenges using three TurtleBot3 Burger robots in ROS2 Humble and Gazebo 11.

본 프로젝트에서는 ROS2 Humble과 Gazebo 11 환경에서 3대의 TurtleBot3 Burger robot을 이용하여 이러한 challenge들을 해결한다.

Each robot independently performs SLAM using SLAM Toolbox. The resulting local occupancy grids are transformed into a common `world` coordinate frame using TF2 and merged into a global `/merged_map`.

각 robot은 SLAM Toolbox를 이용하여 독립적으로 SLAM을 수행한다. 생성된 local occupancy grid는 TF2를 이용하여 공통 `world` coordinate frame으로 transform한 후 global `/merged_map`으로 merge한다.

A LiDAR-based reactive exploration algorithm is also implemented to enable autonomous movement and obstacle avoidance.

또한 autonomous movement와 obstacle avoidance를 수행할 수 있도록 LiDAR-based reactive exploration algorithm을 구현하였다.

---

# Project Objectives

The project was developed incrementally with the following objectives:

본 프로젝트는 다음과 같은 objectives를 단계적으로 구현하는 방식으로 개발하였다.

1. Build a multi-robot simulation environment using TurtleBot3.

   TurtleBot3를 이용하여 multi-robot simulation environment를 구축한다.

2. Configure independent ROS2 namespaces and TF frames for each robot.

   각 robot에 independent ROS2 namespace와 TF frame을 구성한다.

3. Run independent SLAM Toolbox instances for all three robots.

   3대의 robot에서 independent SLAM Toolbox instance를 실행한다.

4. Generate an individual occupancy grid map for each robot.

   각 robot에 대한 individual occupancy grid map을 생성한다.

5. Establish a common `world` coordinate frame for multi-robot map alignment.

   Multi-robot map alignment를 위한 공통 `world` coordinate frame을 구성한다.

6. Transform and merge individual maps into a global `/merged_map`.

   Individual map을 transform하여 global `/merged_map`으로 merge한다.

7. Implement LiDAR-based autonomous movement.

   LiDAR-based autonomous movement를 구현한다.

8. Enable all three robots to perform autonomous exploration simultaneously.

   3대의 robot이 동시에 autonomous exploration을 수행할 수 있도록 구성한다.

9. Evaluate the limitations of reactive exploration and identify directions for future cooperative exploration.

   Reactive exploration의 limitations을 평가하고 향후 cooperative exploration으로 확장하기 위한 방향을 도출한다.

---

# System Architecture

The overall system consists of four major components:

전체 system은 크게 네 가지 major component로 구성된다.

```text
                         Gazebo
                           │
          ┌────────────────┼────────────────┐
          │                │                │
        tb3_0            tb3_1            tb3_2
          │                │                │
        /scan            /scan            /scan
          │                │                │
   SLAM Toolbox     SLAM Toolbox     SLAM Toolbox
          │                │                │
   /tb3_0/map       /tb3_1/map       /tb3_2/map
          │                │                │
          └────────────────┼────────────────┘
                           │
                    TF2 Map Transform
                           │
                     Common World Frame
                           │
                    Multi-Robot Map Merge
                           │
                       /merged_map
                           │
                         RViz2
```text

# Result

The following figure shows the Gazebo simulation and RViz2 visualization during autonomous exploration.

다음 그림은 autonomous exploration 수행 중 Gazebo simulation과 RViz2 visualization을 나타낸다.

<p align="center">
  <img src="Daily%20Log/images/multi_robot_slam_autonomous_exploration.png" width="100%">
</p>

Three TurtleBot3 robots independently perform LiDAR-based reactive exploration while their local SLAM maps are continuously generated and merged into the global `/merged_map`.

3대의 TurtleBot3 robot은 각각 LiDAR-based reactive exploration을 수행하며, 각 robot의 local SLAM map은 지속적으로 생성되고 global `/merged_map`으로 merge된다.

---

# Current Limitation

Although the current system enables three robots to perform autonomous exploration and multi-robot map merging simultaneously, the exploration strategy is based on a simple reactive obstacle avoidance algorithm.

현재 system은 3대의 robot이 동시에 autonomous exploration과 multi-robot map merging을 수행할 수 있지만, exploration strategy는 단순한 reactive obstacle avoidance algorithm을 기반으로 한다.

When an obstacle is detected in front of a robot, the robot compares the left and right free-space distances and turns toward the direction with more available space.

Robot은 전방에서 obstacle을 감지하면 left와 right의 free-space distance를 비교하고, 더 넓은 방향으로 회전한다.

Therefore, the robots can repeatedly revisit the same area instead of systematically selecting unexplored regions.

따라서 robot이 아직 탐색하지 않은 영역을 체계적으로 선택하지 못하고, 동일한 공간을 반복적으로 탐색하는 limitation이 발생한다.

In addition, the current robots do not explicitly coordinate their exploration decisions or divide unexplored areas among themselves.

또한 현재 system에서는 robot 간 exploration decision을 명시적으로 coordinate하거나 unexplored area를 서로 분담하는 기능이 구현되어 있지 않다.

---

# Next Step

To overcome these limitations, the next step is to extend the current reactive exploration into frontier-based autonomous exploration.

이러한 limitation을 해결하기 위해 다음 단계에서는 현재 reactive exploration을 frontier-based autonomous exploration으로 확장한다.

Frontier-based exploration will identify the boundary between explored and unexplored regions and use these frontier regions as candidate exploration targets.

Frontier-based exploration에서는 explored region과 unexplored region의 경계를 frontier로 정의하고, 해당 frontier를 exploration target 후보로 활용한다.

The system can then be further extended to cooperative multi-robot exploration by assigning different frontier targets to different robots based on distance, workload, and exploration efficiency.

이후 각 robot의 distance, workload 및 exploration efficiency를 고려하여 서로 다른 frontier target을 할당함으로써 cooperative multi-robot exploration으로 확장할 수 있다.

The long-term goal is to enable multiple robots to autonomously divide exploration areas, reduce redundant exploration, and improve overall exploration efficiency.

궁극적으로 multiple robot이 exploration area를 autonomous하게 분담하고 redundant exploration을 줄여 전체 exploration efficiency를 향상시키는 것을 목표로 한다.

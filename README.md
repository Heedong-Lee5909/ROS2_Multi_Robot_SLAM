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

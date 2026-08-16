# ROS2 Multi-Robot SLAM

A ROS2-based multi-robot SLAM and autonomous exploration project using three TurtleBot3 robots in a Gazebo indoor environment.

The project focuses on building an independent SLAM pipeline for multiple robots, aligning their local maps in a common world coordinate frame, merging them into a global map, and enabling autonomous exploration using LiDAR-based reactive obstacle avoidance.

---

## Overview

Multi-robot systems can improve exploration efficiency by allowing multiple robots to operate simultaneously in the same environment.

However, deploying multiple SLAM systems introduces several challenges, including:

- Namespace isolation
- Independent TF frames
- Independent LaserScan topics
- Independent SLAM map frames
- Global map alignment
- Multi-robot map merging
- Autonomous robot coordination

This project addresses these challenges using three TurtleBot3 Burger robots in ROS2 Humble and Gazebo 11.

Each robot independently performs SLAM using SLAM Toolbox. The resulting local occupancy grids are transformed into a common `world` coordinate frame using TF2 and merged into a global `/merged_map`.

A LiDAR-based reactive exploration algorithm is also implemented to enable autonomous movement and obstacle avoidance.

---

# Project Objectives

The project was developed incrementally with the following objectives:

1. Build a multi-robot simulation environment using TurtleBot3.
2. Configure independent ROS2 namespaces and TF frames for each robot.
3. Run independent SLAM Toolbox instances for all three robots.
4. Generate an individual occupancy grid map for each robot.
5. Establish a common `world` coordinate frame for multi-robot map alignment.
6. Transform and merge individual maps into a global `/merged_map`.
7. Implement LiDAR-based autonomous movement.
8. Enable all three robots to perform autonomous exploration simultaneously.
9. Evaluate the limitations of reactive exploration and identify directions for future cooperative exploration.

---

# System Architecture

The overall system consists of four major components:

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

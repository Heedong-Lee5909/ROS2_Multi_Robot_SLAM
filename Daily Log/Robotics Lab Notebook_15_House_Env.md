# Day 15 - TurtleBot3 House Environment

---

# Chapter 1. Transition to TurtleBot3 House Environment

## Goal | 목표

기존에는 `empty_world`에서 Multi-Robot을 실행하였다.

이번에는 보다 실제 환경과 유사한 실내 환경에서 Multi-Robot Navigation을 수행하기 위해 `turtlebot3_house.world`로 환경을 변경하였다.

Previously, the multi-robot system was executed in the default empty world.

The objective of this chapter was to migrate the simulation into `turtlebot3_house.world`, providing a more realistic indoor environment for future navigation experiments.

---

## Implementation

기존 `gazebo.launch.py`에서는 Gazebo의 기본 World를 사용하였다.

```python
IncludeLaunchDescription(
    ...
)
```

House World를 사용하도록 수정하였다.

```python
world = os.path.join(
    get_package_share_directory("turtlebot3_gazebo"),
    "worlds",
    "turtlebot3_house.world"
)

IncludeLaunchDescription(
    ...
    launch_arguments={
        "world": world
    }.items()
)
```

---

## Result

실행 결과 Gazebo는

```
Preparing your world...
```

에서 멈추며 로봇이 생성되지 않았다.

---

## Lab Summary

- Gazebo World를 House 환경으로 변경
- Launch Argument를 이용하여 World를 전달

---

# Chapter 2. Gazebo House World Debugging

## Problem

House World는 정상적으로 실행되지 않았으며,

```
Preparing your world...
```

또는

```
Calling service /spawn_entity
```

에서 계속 멈추었다.

또한

```bash
ros2 service list | grep spawn
```

결과에서도 `/spawn_entity`가 생성되지 않았다.

---

## Investigation

Gazebo Server를 확인하였다.

```bash
ps -ef | grep gzserver
```

Factory Plugin 의존성을 확인하였다.

```bash
ldd /opt/ros/humble/lib/libgazebo_ros_factory.so
```

문제가 발견되지 않았다.

Verbose Mode로 Gazebo를 실행하였다.

```bash
gzserver --verbose \
... \
-s libgazebo_ros_factory.so
```

다음 로그가 반복적으로 출력되었다.

```
Getting models from
http://models.gazebosim.org/
```

---

## Root Cause Analysis

House Model 내부를 조사하였다.

```bash
grep "model://" turtlebot3_house.world
```

추가적으로

```bash
grep "uri" model.sdf
```

를 통해 House가 사용하는 모델을 확인하였다.

필요한 모델은

- mailbox
- cafe_table
- first_2015_trash_can
- table_marble

이었다.

하지만 로컬에는

```
cafe_table
```

모델이 존재하지 않았다.

Gazebo는 해당 모델을 온라인에서 다운로드하려고 시도하였고,

초기화가 완료되지 않아 `/spawn_entity` 서비스가 생성되지 않았다.

---

## Solution

Gazebo Models Repository를 다운로드하였다.

```bash
git clone https://github.com/osrf/gazebo_models.git
```

필요한 모델만 복사하였다.

```bash
cp -r gazebo_models/cafe_table ~/.gazebo/models/
```

확인 결과

```
~/.gazebo/models

cafe_table
mailbox
table_marble
first_2015_trash_can
```

가 모두 존재하였다.

이후 House World가 정상적으로 로드되었다.

---

## Lab Summary

- House Model 의존성 분석
- Missing Model 확인
- cafe_table 추가
- Gazebo 정상 실행

---

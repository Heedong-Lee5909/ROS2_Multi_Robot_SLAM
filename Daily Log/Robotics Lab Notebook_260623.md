# TurtleBot3 Gazebo Setup and Troubleshooting (터틀봇3 Gazebo 설치 및 문제 해결)

## Date (날짜)

2026-06-23

---

# Objective (목표)

Set up a TurtleBot3 Gazebo simulation environment on ROS2 Humble and prepare for future Multi-Robot SLAM experiments.

ROS2 Humble 환경에서 TurtleBot3 Gazebo 시뮬레이션을 구축하고 향후 Multi-Robot SLAM 실습을 위한 개발 환경을 준비한다.

---

# Development Environment (개발 환경)

| Item           | Description       |
| -------------- | ----------------- |
| OS             | Ubuntu 22.04      |
| ROS            | ROS2 Humble       |
| Simulator      | Gazebo 11         |
| Virtualization | VMware            |
| Robot          | TurtleBot3 Burger |

---

# Step 1. Launch TurtleBot3 Gazebo (TurtleBot3 Gazebo 실행)

### Set TurtleBot3 model (TurtleBot3 모델 설정)

```bash
export TURTLEBOT3_MODEL=burger
```

**English**

Specify which TurtleBot3 model will be used in the simulation.

**한국어**

시뮬레이션에서 사용할 TurtleBot3 모델을 지정한다.

---

### Launch Gazebo Simulation (Gazebo 시뮬레이션 실행)

```bash
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

**English**

Launch Gazebo and spawn the TurtleBot3 robot.

**한국어**

Gazebo를 실행하고 TurtleBot3 로봇을 생성한다.

---

# Step 2. Problem Encountered (문제 발생)

### Error Message (에러 메시지)

```text
gzclient:
boost::shared_ptr<Camera>

Assertion `px != 0' failed.
```

```text
[gzclient-2]: process has died
```

**English**

Gazebo server started successfully, but the Gazebo GUI (gzclient) crashed immediately after spawning the robot.

**한국어**

Gazebo 서버는 정상적으로 실행되었지만 로봇 생성 직후 Gazebo GUI(gzclient)가 비정상 종료되었다.

---

# Step 3. Investigation (원인 분석)

## Verify Gazebo Installation (Gazebo 설치 상태 확인)

```bash
gazebo --verbose
```

### Purpose (목적)

Check whether Gazebo itself is working correctly.

Gazebo 자체가 정상 동작하는지 확인한다.

### Result (결과)

* Empty world loaded successfully.

* Gazebo GUI launched successfully.

* Empty World 정상 로딩

* Gazebo GUI 정상 실행

---

## Check OpenGL Renderer (OpenGL 렌더러 확인)

```bash
glxinfo | grep "OpenGL renderer"
```

### Purpose (목적)

Identify which graphics renderer Gazebo is using.

Gazebo가 어떤 그래픽 렌더러를 사용하는지 확인한다.

### Result (결과)

```text
OpenGL renderer string: SVGA3D
```

**English**

The virtual machine is using VMware's virtual graphics driver.

**한국어**

VMware 가상 그래픽 드라이버(SVGA3D)를 사용 중임을 확인하였다.

---

## Verify Virtualization Platform (가상화 플랫폼 확인)

```bash
systemd-detect-virt
```

### Result (결과)

```text
vmware
```

**English**

Confirmed that the environment is running inside VMware.

**한국어**

현재 Ubuntu가 VMware 환경에서 실행 중임을 확인하였다.

---

# Step 4. Solution (해결 방법)

### Configure Gazebo Resource Path (Gazebo 리소스 경로 설정)

```bash
export GAZEBO_RESOURCE_PATH=/usr/share/gazebo-11:$GAZEBO_RESOURCE_PATH
```

### Purpose (목적)

Tell Gazebo where to search for world files, models, textures, and rendering resources.

Gazebo가 World 파일, 모델, 텍스처, 렌더링 리소스를 검색할 경로를 지정한다.

### Result (결과)

After applying this environment variable, TurtleBot3 Gazebo launched successfully.

해당 환경변수 설정 후 TurtleBot3 Gazebo가 정상적으로 실행되었다.

---

# Environment Variables Learned Today (오늘 학습한 환경 변수)

## TURTLEBOT3_MODEL

```bash
export TURTLEBOT3_MODEL=burger
```

### English

Specifies which TurtleBot3 model will be loaded.

### 한국어

사용할 TurtleBot3 모델을 지정한다.

Available Models (사용 가능한 모델)

* burger
* waffle
* waffle_pi

---

## GAZEBO_RESOURCE_PATH

```bash
export GAZEBO_RESOURCE_PATH=/usr/share/gazebo-11:$GAZEBO_RESOURCE_PATH
```

### English

Defines directories that Gazebo searches for resources such as worlds, models, textures, and shaders.

### 한국어

Gazebo가 World, Model, Texture, Shader 등의 리소스를 검색할 디렉토리를 지정한다.

---

## LIBGL_ALWAYS_SOFTWARE

```bash
export LIBGL_ALWAYS_SOFTWARE=1
```

### English

Forces OpenGL rendering to use CPU-based software rendering instead of GPU acceleration.

### 한국어

GPU 대신 CPU 기반 소프트웨어 렌더링을 강제로 사용한다.

### Note (참고)

This variable was tested during troubleshooting but was not required for the final solution.

문제 해결 과정에서 테스트하였으나 최종 해결에는 필요하지 않았다.

---

# Final Outcome (최종 결과)

### Successfully Completed (성공 항목)

* TurtleBot3 Gazebo launch

* Gazebo GUI execution

* TurtleBot3 Burger spawning

* ROS2–Gazebo integration verification

* TurtleBot3 Gazebo 실행 성공

* Gazebo GUI 실행 성공

* TurtleBot3 Burger 생성 성공

* ROS2–Gazebo 연동 확인

---


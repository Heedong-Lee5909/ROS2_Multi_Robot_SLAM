# 05. Refactoring Launch Files & Automatic Multi-Robot Generation

## Objective

Refactor the multi-robot launch file to eliminate duplicated code and automatically generate multiple robots using Python functions and loops.

중복된 Launch 코드를 함수와 반복문으로 리팩토링하여 여러 대의 Robot을 자동으로 생성하는 구조를 구현하는 것을 목표로 한다.

---

# 1. Refactoring with Functions

Previously, each robot required a separate `Node()` definition.

기존에는 Robot마다 `Node()`를 직접 작성하였다.

```python
Node(...)
Node(...)
Node(...)
```

To eliminate duplicated code, a helper function was created.

중복 코드를 제거하기 위해 Robot 생성 함수를 작성하였다.

```python
def spawn_robot(name, namespace, x, y):
```

---

# 2. Returning a Node

The helper function returns a `Node` object.

함수는 Robot을 생성하는 `Node` 객체를 반환한다.

```python
return Node(
    package="gazebo_ros",
    executable="spawn_entity.py",
    ...
)
```

### Purpose

Encapsulate robot creation logic into a reusable function.

Robot 생성 로직을 하나의 함수로 재사용하기 위함이다.

---

# 3. Parameterizing Robot Information

Instead of hardcoding robot information inside the launch file, the following values became function parameters.

Robot 정보를 코드 내부에 직접 작성하지 않고 함수의 입력으로 변경하였다.

```python
name
namespace
x
y
```

Only robot-specific information changes.

Robot마다 달라지는 정보만 입력받도록 설계하였다.

---

# 4. Simplified Launch File

Previous

```python
Node(...)
Node(...)
Node(...)
```

↓

Refactored

```python
spawn_robot("burger_1", "tb3_0", 0, 0)
spawn_robot("burger_2", "tb3_1", 2, 2)
spawn_robot("burger_3", "tb3_2", 4, 4)
```

The launch file became significantly shorter and easier to read.

Launch File의 가독성과 재사용성이 향상되었다.

---

# 5. Separating Data from Logic

Instead of directly calling `spawn_robot()`, robot information was stored separately.

Robot 생성 코드와 Robot 데이터를 분리하였다.

```python
robots = [
    ("burger_1", "tb3_0", 0, 0),
    ("burger_2", "tb3_1", 2, 2),
    ("burger_3", "tb3_2", 4, 4),
]
```

### Benefit

Robot information can be modified without changing launch logic.

Launch 로직을 수정하지 않고 Robot 정보만 변경할 수 있다.

---

# 6. Automatic Robot Creation

Robots are created using a loop.

반복문을 이용하여 Robot을 자동 생성하였다.

```python
for name, namespace, x, y in robots:
    actions.append(
        spawn_robot(name, namespace, x, y)
    )
```

### Purpose

Automatically create all robots stored in the list.

Robot 목록만 변경하면 Launch File은 수정할 필요가 없다.

---

# 7. Automatic Robot List Generation

Instead of manually writing every robot, the robot list is automatically generated.

Robot 목록도 자동 생성하도록 개선하였다.

```python
NUM_ROBOTS = 3

robots = []

for i in range(NUM_ROBOTS):
    robots.append(
        (
            f"burger_{i+1}",
            f"tb3_{i}",
            i * SPACING,
            i * SPACING,
        )
    )
```

---

# 8. Configurable Robot Spacing

Added a configurable spacing variable.

Robot 간 간격을 변수로 관리하였다.

```python
SPACING = 2.0
```

```python
i * SPACING
```

### Benefit

Changing only one variable automatically updates the spacing of every robot.

변수 하나만 수정하면 모든 Robot의 생성 위치가 변경된다.

---

# 9. Final Launch Flow

```
NUM_ROBOTS
        │
        ▼
Generate Robot List
        │
        ▼
for Loop
        │
        ▼
spawn_robot()
        │
        ▼
Node()
        │
        ▼
Gazebo
```

---

# Key Concepts Learned

- Functions eliminate duplicated code.
- `Node()` objects can be returned from functions.
- Robot-specific information should be separated from launch logic.
- Lists can store robot configuration.
- Loops automatically create multiple robots.
- Parameters improve code reusability.
- Separating data and logic makes the launch file scalable.

---

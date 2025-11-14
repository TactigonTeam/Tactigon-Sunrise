# Sunrise Middleware - ARISE Project POC

Release date: 14/11/2025

Author: Stefano Barbareschi

Release version:
 - sunrise: 0.0.1
 - sunrise_msgs: 0.0.1 (tactigon-gear 5.4.2)

Change Log:
 - Created sunrise package containing mission_controller and sunrise_bridge nodes
    - TEO can save and load skills using JSON file
    - LEO is just a placeholder
 - Created sunrise_msgs message definition
 - Added build files to compile the ROS2 package
 - Added MODEL_01_R for tactigon gesture recognition
 - Added base configuration files

## Introduction

The **Sunrise** project is part of the European **ARISE** program (Agile, human-centric, and Real-time enabled Open Source technologies) and represents a **middleware for multimodal human-robot interaction (HRI)**.
Its goal is to create a software layer capable of receiving multimodal inputs (camera, voice, gestures, and custom input from the **Tactigon-Skin** wearable), normalizing them, and managing them through a **Mission Controller** that coordinates robot action execution.

The first **Proof of Concept (POC)** allows:

* Receiving tasks composed of **skills** (e.g., `pick from position workbench #1`) sent by an operator.
* Saving individual skills.
* Forwarding data to a robot for action execution.

## Architecture and Components

The ROS2 package `sunrise` contains two main nodes:

### 1. `mission_controller`

* Receives **intent** and **action** messages.
* Saves individual **skills**.
* Manages tasks and their sequence.
* Acts as the logical core of the middleware.

### 2. `sunrise_bridge`

* Acts as a **bridge** for data coming from the **Tactigon-Skin** device.
* Handles **gesture** and **touch** input.
* Normalizes data and forwards it to the **mission_controller**.

## Technologies Used

* **Python 3.12**
* **ROS 2 Jazzy** on **Ubuntu**
* **colcon build** for ROS2 package compilation
* **Tactigon-Skin SDK** (`tactigon_gear`) for wearable input management

## Installation and Setup

Follow these steps to clone, install, and build the project:

### 1. Clone the repository

```bash
git clone https://github.com/TactigonTeam/Tactigon-Sunrise.git
cd Tactigon-Sunrise
```
### 2. Install Tactigon package globally

> ⚠️ **Important:** For `sunrise_bridge` to work, you must install `tactigon_gear==5.2.4` globally via `pip`. On Ubuntu, global package installation is disabled by default, so `sudo` is required.

```bash
pip3 install tactigon-gear==5.2.4 --break-system-packages
```

### 3. Build ROS2 packages with colcon

```bash
# Ensure you are in the ROS2 workspace root
colcon build --symlink-install
```

### 4. Source the ROS2 environment

```bash
source install/setup.bash
```

### 5. Run the nodes

* Start the **mission_controller**:

```bash
ros2 run sunrise mission_controller config/mission_controller.json
```

* Start the **sunrise_bridge**:

```bash
ros2 run sunrise sunrise_bridge config/sunrise_bridge.json
```

## Sunrise Messages - `sunrise_msgs`

The `sunrise_msgs` package defines the core message types used in the **Sunrise Middleware**. These messages enable communication between nodes such as `mission_controller` and `sunrise_bridge` and can be **easily extended** for future functionalities.

Currently, two message types are defined: `Action.msg` and `Intent.msg`.

### Action.msg

The `Action` message represents a single action or event captured by the middleware. It supports multiple types of inputs, including gestures, voice commands, touch events, and camera points.

#### Enum-like constants

```text
int8 GESTURE = 0
int8 VOICE_COMMAND = 1
int8 TOUCH = 2
int8 CAMERA_POINT = 3
```

#### Fields

| Field   | Type   | Description                                                                |
| ------- | ------ | -------------------------------------------------------------------------- |
| type    | int8   | The type of action (GESTURE, VOICE_COMMAND, TOUCH, CAMERA_POINT)           |
| payload | string | The payload content of the action (e.g., gesture name, voice command text) |

#### Example Usage

```python
from sunrise_msgs.msg import Action

action = Action()
action.type = Action.GESTURE
action.payload = 'swipe_up'
```

### Intent.msg

The `Intent` message represents the high-level intent of the operator, such as teaching the robot a new task or instructing it to repeat a task.

#### Enum-like constants

```text
int8 TEACH = 0
int8 REPEAT = 1
```

#### Fields

| Field   | Type   | Description                                        |
| ------- | ------ | -------------------------------------------------- |
| type    | int8   | The type of intent (TEACH, REPEAT)                 |
| payload | string | The payload content, e.g., task name or parameters |

#### Example Usage

```python
from sunrise_msgs.msg import Intent

intent = Intent()
intent.type = Intent.TEACH
intent.payload = 'pick from position workbench #1'
```

## Extensibility

Both `Action` and `Intent` messages are designed to be **extended** with additional types or fields in the future as new sensors or modalities are integrated. When adding new constants, ensure their values do not conflict with existing ones to maintain backward compatibility.


## Additional Notes

* Tasks and skills are currently stored in JSON files; future implementations may include saving to a database.
* The middleware is modular and easily extendable to other multimodal input types (voice commands, camera-based object detection, custom sensors).
* Integration with physical robots can be added later via ROS2 topics or action servers.

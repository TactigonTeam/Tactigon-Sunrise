# Sunrise Middleware - ARISE Project POC

Company: Next Industries s.r.l

Release date: 14/11/2025

Author: Stefano Barbareschi

Release version:
 - sunrise: 0.0.1
 - sunrise_msgs: 0.0.1 (tactigon-gear 5.5.2)

Change Log:
 - Created sunrise package containing mission_controller and sunrise_bridge nodes
    - TEO can save and load skills using JSON file
    - LEO is just a placeholder
 - Created sunrise_msgs message definition
 - Added build files to compile the ROS2 package
 - Added MODEL_01_R for tactigon gesture recognition
 - Added base configuration files
 - Added sunrise_braccio, sunrise_comau, sunrise_tactigon, sunrise_tactigon_mock nodes
 - Added sunrise_fiware FIWARE monitoring subsystem
 - Added sunrise_robot COMAU Racer 7 driver container
 - Updated QoS profiles across all nodes

## Introduction

The **Sunrise** project is part of the European **ARISE** program (Agile, human-centric, and Real-time enabled Open Source technologies) and represents a **middleware for multimodal human-robot interaction (HRI)**.
Its goal is to create a software layer capable of receiving multimodal inputs (camera, voice, gestures, and custom input from the **Tactigon-Skin** wearable), normalizing them, and managing them through a **Mission Controller** that coordinates robot action execution.

The first **Proof of Concept (POC)** allows:

* Receiving tasks composed of **skills** (e.g., `pick from position workbench #1`) sent by an operator.
* Saving and replaying individual skills via TEO.
* Forwarding joint trajectory commands to a robot for action execution via LEO.
* Monitoring the system in real-time via FIWARE and Grafana.

## Architecture and Components

```
+-----------------------------------------------------------------------------+
|                          Sunrise Middleware                                 |
|                                                                             |
|  +-----------------+     Gesture/Touch/Voice   +-------------------------+  |
|  | sunrise_tactigon | ───────────────────────> |                         |  |
|  | (or _mock)       |  /human/body/.../gesture |    sunrise_bridge       |  |
|  +-----------------+  /human/voices/.../speech +----------+-------------+   |
|                                                           | Action/Intent   |
|                                                +----------v-------------+   |
|  +------------------+  BraccioCommand          |                        |   |
|  |  sunrise_braccio | <─────────────────────── |   mission_controller   |   |
|  +------------------+                          |   (TEO + LEO)          |   |
|                                                |                        |   |
|  +------------------+  BraccioJointCommand    +-----------+-------------+   |
|  |   sunrise_comau  | <────────────────────────────────────+                |
|  +--------+---------+                                                       |
|           | ExecuteJointTrajectory (ROS2 Action)                            |
|           v                                                                 |
|  +--------------------+                                                     |
|  |  sunrise_robot     |  (COMAU Racer 7 driver - separate container)        |
|  +--------------------+                                                     |
|                                                                             |
|  +------------------------------------------------------------------------+ |
|  |  sunrise_fiware  (Integration Service -> FIWARE Orion-LD -> Grafana)   | |
|  +------------------------------------------------------------------------+ |
+-----------------------------------------------------------------------------+
```

![Sunrise Architecture](https://github.com/TactigonTeam/Tactigon-Sunrise/blob/master/docs/img/sunrise_architecture.jpg)

---

## ROS 2 Nodes

### 1. `mission_controller`

The logical core of the middleware. It implements a state machine (`IDLE -> TEACH -> REPEAT`) and orchestrates all human-robot interaction.

**Entry point:** `ros2 run sunrise mission_controller config/mission_controller.json`

**Subscriptions:**

| Topic | Type | QoS |
|-------|------|-----|
| `/sunrise/mission_controller/intent` (configurable) | `sunrise_msgs/Intent` | RELIABLE, VOLATILE, KEEP_LAST(10) |
| `/sunrise/mission_controller/action` (configurable) | `sunrise_msgs/Action` | RELIABLE, VOLATILE, KEEP_LAST(10) |

**Publications:**

| Topic | Type | QoS |
|-------|------|-----|
| `/sunrise/mission_controller/log` (configurable) | `rcl_interfaces/Log` | RELIABLE, VOLATILE, KEEP_LAST(10) |
| Robot command topics (from `mission_controller_student.json`) | `BraccioCommand` / `BraccioJointCommand` | RELIABLE, VOLATILE, KEEP_LAST(1) |

#### TEO - Teach Engine Orchestrator

TEO is embedded in `mission_controller` and is responsible for **recording operator skills** (sequences of robot movements) and persisting them to the teacher config JSON file. Skills are grouped into named tasks.

#### LEO - Learn Engine Orchestrator

LEO is embedded in `mission_controller` and is responsible for **replaying tasks** by reading the student config JSON file and dispatching robot commands to the configured command topics.

---

### 2. `sunrise_bridge`

Translates normalized Tactigon gestures and voice transcriptions into `Action` and `Intent` messages forwarded to the `mission_controller`. It acts as the semantic interpretation layer between raw input and robot control.

**Entry point:** `ros2 run sunrise sunrise_bridge config/sunrise_bridge.json`

**Subscriptions:**

| Topic | Type | QoS |
|-------|------|-----|
| `/human/body/person1/gesture` | `sunrise_msgs/Gesture` | BEST_EFFORT, VOLATILE, KEEP_LAST(5) |
| `/human/voices/person1/livespeech` | `sunrise_msgs/Transcription` | BEST_EFFORT, VOLATILE, KEEP_LAST(5) |

**Publications:**

| Topic | Type | QoS |
|-------|------|-----|
| `action_topic` (configurable, default `/sunrise/mission_controller/action`) | `sunrise_msgs/Action` | RELIABLE, VOLATILE, KEEP_LAST(10) |
| `intent_topic` (configurable, default `/sunrise/mission_controller/intent`) | `sunrise_msgs/Intent` | RELIABLE, VOLATILE, KEEP_LAST(10) |
| `/human/voice/person1/stream` | `std_msgs/String` | RELIABLE, VOLATILE, KEEP_LAST(1) |

Gesture and touch inputs are mapped to `ACTION`, `TEACH_SKILL`, `TEACH_TASK`, `REPEAT_SKILL`, `REPEAT_TASK`, or `SPEECH` via the `sunrise_bridge.json` configuration.

---

### 3. `sunrise_braccio`

ROS 2 driver for the **Arduino Braccio** robotic arm. Connects over Bluetooth using the `tactigon_arduino_braccio` library, receives Cartesian commands, and publishes the movement result.

**Entry point:** `ros2 run sunrise sunrise_braccio config/sunrise_braccio.json`

**Subscriptions:**

| Topic | Type | QoS |
|-------|------|-----|
| `command_topic` (configurable, default `/robot/braccio/command`) | `sunrise_msgs/BraccioCommand` | RELIABLE, VOLATILE, KEEP_LAST(1) |

**Publications:**

| Topic | Type | QoS |
|-------|------|-----|
| `response_topic` (configurable, default `robot/braccio/response`) | `sunrise_msgs/BraccioResponse` | RELIABLE, VOLATILE, KEEP_LAST(1) |

---

### 4. `sunrise_comau`

ROS 2 action client that interfaces with the **COMAU Racer 7** robot via the `comau_msgs/ExecuteJointTrajectory` action server exposed by `sunrise_robot`. Translates `BraccioJointCommand` messages (joint trajectory arrays in radians) into ROS 2 action goals.

**Entry point:** `ros2 run sunrise sunrise_comau config/sunrise_comau.json`

**Subscriptions:**

| Topic | Type | QoS |
|-------|------|-----|
| `command_topic` (configurable, default `/robot/comau/action`) | `sunrise_msgs/BraccioJointCommand` | RELIABLE, VOLATILE, KEEP_LAST(1) |

**Publications:**

| Topic | Type | QoS |
|-------|------|-----|
| `response_topic` (configurable, default `/robot/comau/action_result`) | `comau_msgs/ActionResult` | RELIABLE, VOLATILE, KEEP_LAST(1) |

**Action client:**

| Action server | Type |
|--------------|------|
| `/execute_joint_trajectory_handler` | `comau_msgs/ExecuteJointTrajectory` |

---

### 5. `sunrise_tactigon`

Hardware driver for the **Tactigon-Skin** wearable device. Connects to the device over Bluetooth via a local socket server (`tactigon-speech-socket` container), captures gestures, touch events, and voice transcriptions, and publishes them as ROS4HRI-compliant topics.

**Entry point:** `ros2 run sunrise sunrise_tactigon config/sunrise_tactigon.json`

**Publications:**

| Topic | Type | QoS | Description |
|-------|------|-----|-------------|
| `/human/body/person1/gesture` | `sunrise_msgs/Gesture` | BEST_EFFORT, VOLATILE, KEEP_LAST(5) | Hand gestures (`type=HAND`) and touch events (`type=TOUCH`) from the Tactigon-Skin |
| `/human/voices/person1/livespeech` | `sunrise_msgs/Transcription` | BEST_EFFORT, VOLATILE, KEEP_LAST(5) | In-progress and completed voice transcriptions |

**Subscriptions:**

| Topic | Type | QoS | Description |
|-------|------|-----|-------------|
| `/human/voice/person1/stream` | `std_msgs/String` | RELIABLE, VOLATILE, KEEP_LAST(1) | Triggers on-device speech recognition |

The node runs at 50 Hz (0.02 s timer). Gesture recognition uses a pre-trained scikit-learn model (`data/models/MODEL_01_R/model.pickle`). Speech recognition uses a hierarchical hotword grammar defined in `sunrise_tactigon.json`.

#### Tactigon-Skin Topics Detail

`Gesture.msg` carries both hand gestures and touch events via the `type` field:

```text
int8 HAND  = 0   # recognized gesture from IMU model (e.g. "up", "down", "twist")
int8 TOUCH = 1   # capacitive touch event (e.g. "SINGLE_TAP", "TWO_FINGER_TAP")

int8 type
string payload   # gesture/touch name as string
```

`Transcription.msg` carries speech recognition output:

```text
string text_so_far    # partial result updated in real-time
string transcription  # final recognized sentence
string[] path         # sequence of hotwords matched in the grammar tree
float64 time          # recognition duration in seconds
bool timeout          # true if the recognition timed out
```

---

### 6. `sunrise_tactigon_mock`

A **PyQt5 GUI application** that emulates the Tactigon-Skin hardware, publishing gesture and voice transcription messages without requiring the physical device. Designed for development, testing, and CI/CD pipelines.

**Entry point:** `ros2 run sunrise sunrise_mock`

**Publications:**

| Topic | Type | QoS |
|-------|------|-----|
| `/human/body/person1/gesture` | `sunrise_msgs/Gesture` | BEST_EFFORT, VOLATILE, KEEP_LAST(5) |
| `/human/voices/person1/livespeech` | `sunrise_msgs/Transcription` | BEST_EFFORT, VOLATILE, KEEP_LAST(5) |

The GUI allows manual injection of gestures (`HAND` / `TOUCH`) with a custom payload string, as well as voice transcriptions (partial and final), enabling full integration testing of `sunrise_bridge` and `mission_controller` without any hardware.

---

### 7. `camera_tracking`

Performs real-time ArUco marker tracking from a camera feed and publishes detected marker positions. Used by the operator to define spatial targets in the workspace.

**Configuration:** `config/camera_tracking.json`

**Subscriptions:**

| Topic | Type | QoS |
|-------|------|-----|
| `/camera/image_raw` (configurable) | `sensor_msgs/Image` | BEST_EFFORT, VOLATILE, KEEP_LAST(1) |

**Publications:**

| Topic | Type | QoS |
|-------|------|-----|
| `/camera_tracking/image` (configurable) | `sensor_msgs/Image` | BEST_EFFORT, VOLATILE, KEEP_LAST(1) |
| `/camera_tracking/markers` (configurable) | `sunrise_msgs/MarkerList` | RELIABLE, VOLATILE, KEEP_LAST(10) |
| `/camera_tracking/pointing` (configurable) | `sunrise_msgs/Marker` | RELIABLE, VOLATILE, KEEP_LAST(10) |

Camera parameters are configured via ROS 2 parameters in `config/ros2/parameters/cfg_test.yaml` (640x480 @ 15 fps, MJPEG format).

---

## Complete Topic Reference

| Topic | Type | Publisher | Subscriber | QoS |
|-------|------|-----------|------------|-----|
| `/human/body/person1/gesture` | `Gesture` | `sunrise_tactigon` / `sunrise_tactigon_mock` | `sunrise_bridge` | BEST_EFFORT, VOLATILE, KEEP_LAST(5) |
| `/human/voices/person1/livespeech` | `Transcription` | `sunrise_tactigon` / `sunrise_tactigon_mock` | `sunrise_bridge` | BEST_EFFORT, VOLATILE, KEEP_LAST(5) |
| `/human/voice/person1/stream` | `std_msgs/String` | `sunrise_bridge` | `sunrise_tactigon` | RELIABLE, VOLATILE, KEEP_LAST(1) |
| `/sunrise/mission_controller/action` | `Action` | `sunrise_bridge` | `mission_controller` | RELIABLE, VOLATILE, KEEP_LAST(10) |
| `/sunrise/mission_controller/intent` | `Intent` | `sunrise_bridge` | `mission_controller` | RELIABLE, VOLATILE, KEEP_LAST(10) |
| `/sunrise/mission_controller/log` | `rcl_interfaces/Log` | `mission_controller` | Integration Service | RELIABLE, VOLATILE, KEEP_LAST(10) |
| `/robot/braccio/command` | `BraccioCommand` | `mission_controller` (LEO) | `sunrise_braccio` | RELIABLE, VOLATILE, KEEP_LAST(1) |
| `robot/braccio/response` | `BraccioResponse` | `sunrise_braccio` | `mission_controller` | RELIABLE, VOLATILE, KEEP_LAST(1) |
| `/robot/comau/action` | `BraccioJointCommand` | `mission_controller` (LEO) | `sunrise_comau` | RELIABLE, VOLATILE, KEEP_LAST(1) |
| `/robot/comau/action_result` | `comau_msgs/ActionResult` | `sunrise_comau` | `mission_controller` | RELIABLE, VOLATILE, KEEP_LAST(1) |
| `/execute_joint_trajectory_handler` | `ExecuteJointTrajectory` (Action) | `sunrise_robot` driver | `sunrise_comau` | ROS 2 Action (RELIABLE) |
| `/camera/image_raw` | `sensor_msgs/Image` | Camera driver | `camera_tracking` | BEST_EFFORT, VOLATILE, KEEP_LAST(1) |
| `/camera_tracking/image` | `sensor_msgs/Image` | `camera_tracking` | -- | BEST_EFFORT, VOLATILE, KEEP_LAST(1) |
| `/camera_tracking/markers` | `MarkerList` | `camera_tracking` | `mission_controller` | RELIABLE, VOLATILE, KEEP_LAST(10) |
| `/camera_tracking/pointing` | `Marker` | `camera_tracking` | Integration Service | RELIABLE, VOLATILE, KEEP_LAST(10) |
| `/sunrise_app/bridge/action` | `Action` | `sunrise_bridge` | Integration Service | RELIABLE, VOLATILE, KEEP_LAST(10) |
| `/sunrise_app/bridge/intent` | `Intent` | `sunrise_bridge` | Integration Service | RELIABLE, VOLATILE, KEEP_LAST(10) |
| `/sunrise/telemetry/setup_time` | `std_msgs/Float64` | Telemetry node | `ros_to_db_bridge` | BEST_EFFORT, VOLATILE, KEEP_LAST(1) |
| `/sunrise/telemetry/job_success_rate` | `std_msgs/Float64` | Telemetry node | `ros_to_db_bridge` | BEST_EFFORT, VOLATILE, KEEP_LAST(1) |
| `/sunrise/telemetry/retries` | `std_msgs/Float64` | Telemetry node | `ros_to_db_bridge` | BEST_EFFORT, VOLATILE, KEEP_LAST(1) |
| `/sunrise/telemetry/downtime` | `std_msgs/Float64` | Telemetry node | `ros_to_db_bridge` | BEST_EFFORT, VOLATILE, KEEP_LAST(1) |
| `/sunrise/telemetry/time_to_recall_db` | `std_msgs/Float64` | Telemetry node | `ros_to_db_bridge` | BEST_EFFORT, VOLATILE, KEEP_LAST(1) |

---

## FIWARE Monitoring System (`sunrise_fiware`)

`sunrise_fiware` is the real-time monitoring subsystem of the Sunrise middleware. It uses the **FIWARE** platform to collect data from ROS 2 nodes and forward it to a **Grafana** dashboard via a **TimescaleDB** time-series database.

### Architecture

```
ROS 2 Topics
     |
     v  (Integration Service - Dynamic ROS2/FIWARE bridge)
FIWARE Orion-LD  <-- eProsima Integration Service
     |  (TRoE - Temporal Representation of Entities)
     v
TimescaleDB (PostgreSQL)  <-- Mintaka (NGSI-LD Temporal API)
     |
     v
Grafana Dashboard (http://localhost:3000)
```

### Services (Docker Compose)

| Container | Image | Port | Description |
|-----------|-------|------|-------------|
| `fiware-orion` | `fiware/orion-ld:latest` | 1026 | NGSI-LD Context Broker with TRoE enabled |
| `mongodb` | `mongo:4.4` | 27017 | MongoDB backend for Orion-LD |
| `sunrise-timescaledb` | `timescale/timescaledb:latest-pg17` | 5432 | Time-series database for TRoE and telemetry |
| `sunrise-mintaka` | `fiware/mintaka:0.6.18` | 8080 | NGSI-LD Temporal Retrieval API |
| `sunrise-grafana` | `grafana/grafana:latest` | 3000 | Dashboard (Infinity datasource plugin) |
| `integration-service` | custom | -- | eProsima Integration Service (ROS2 to FIWARE bridge) |

### Monitored ROS 2 Topics

The Integration Service forwards the following topics to FIWARE Orion-LD:

| ROS 2 Topic | Type | FIWARE Entity |
|------------|------|---------------|
| `/sunrise_app/bridge/intent` | `Intent` | Intent entity |
| `/sunrise_app/bridge/action` | `Action` | Action entity |
| `/camera_tracking/pointing` | `Marker` | Marker entity |
| `/human/body/person1/gesture` | `Gesture` | Gesture entity |
| `/human/voices/person1/livespeech` | `Transcription` | Transcription entity |

Telemetry topics (`/sunrise/telemetry/*`) are consumed directly by `ros_to_db_bridge.py`, which writes metrics to TimescaleDB table `telemetria_robot`:

- `/sunrise/telemetry/setup_time`
- `/sunrise/telemetry/job_success_rate`
- `/sunrise/telemetry/retries`
- `/sunrise/telemetry/downtime`
- `/sunrise/telemetry/time_to_recall_db`
- `/sunrise/telemetry/ventilator_manufactured`
- `/sunrise/telemetry/defect_ventilator`
- `/sunrise/telemetry/job_recall_number`

### Starting the Monitoring Stack

```bash
cd sunrise_fiware
docker compose up -d
```

Grafana is available at http://localhost:3000 (default credentials: `admin` / `admin`).

---

## `sunrise_robot` - COMAU Racer 7 Driver

`sunrise_robot` is a dedicated Docker container running the ROS 2 driver for the **COMAU Racer 7-1.4** collaborative robot arm.

The driver is based on the official **COMAU ROS 2 Driver** available at:
> https://github.com/Comau/COMAU-ROS2-DRIVER/tree/main

We have **forked and customized** this driver to work with our specific configuration:
- Configured for the `racer7-14` model (`ROBOT_MODEL=racer7-14`)
- Fixed include path issues for `joint_limits` on Ubuntu 22.04
- Integrated with the `comau_msgs/ExecuteJointTrajectory` action interface used by `sunrise_comau`
- Built on `eprosima/vulcanexus:humble-base` (ROS 2 Humble)

> **Note:** The COMAU driver container runs ROS 2 **Humble** while the main Sunrise container runs ROS 2 **Jazzy**. Both containers use `network_mode: host` and share `ROS_DOMAIN_ID=0`, so they can communicate transparently over DDS.

**Starting the COMAU driver:**

```bash
docker compose up sunrise-comau
```

The driver exposes the `/execute_joint_trajectory_handler` ROS 2 action server that `sunrise_comau` connects to.

---

## ROS 2 / Vulcanexus Interfaces

### Runtime Environment

All containers in this project are based on **eProsima Vulcanexus**, which bundles:
- **ROS 2** (Jazzy for `sunrise`, Humble for `sunrise_robot` and `integration-service`)
- **Fast-DDS** as the default DDS middleware
- **eProsima Integration Service** for protocol bridging

### Environment Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `ROS_DOMAIN_ID` | `0` | All nodes belong to the same DDS domain |
| `RMW_IMPLEMENTATION` | `rmw_fastrtps_cpp` | Default RMW (Fast-DDS, set by Vulcanexus) |
| `ROBOT_MODEL` | `racer7-14` | COMAU robot model identifier |

### Recommended DDS Configuration

The recommended Fast-DDS profile for this system uses the **Simple Discovery Protocol** with host-only interfaces (all containers run `network_mode: host`). No explicit XML profile is required for local single-machine deployments.

For multi-machine deployments, create a `fastdds_profile.xml` and set `FASTRTPS_DEFAULT_PROFILES_FILE`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<profiles xmlns="http://www.eprosima.com/XMLSchemas/fastRTPS_Profiles">
  <participant profile_name="default_participant" is_default_profile="true">
    <rtps>
      <builtin>
        <discovery_config>
          <discoveryProtocol>SIMPLE</discoveryProtocol>
          <use_SIMPLE_EndpointDiscoveryProtocol>true</use_SIMPLE_EndpointDiscoveryProtocol>
          <EDP>SIMPLE</EDP>
        </discovery_config>
        <metatrafficUnicastLocatorList>
          <locator>
            <udpv4>
              <address>0.0.0.0</address>
            </udpv4>
          </locator>
        </metatrafficUnicastLocatorList>
      </builtin>
    </rtps>
  </participant>
</profiles>
```

---

## FIWARE Interfaces

### NGSI-LD API

Orion-LD exposes the NGSI-LD REST API at `http://localhost:1026`.

**Query all entities:**
```bash
curl http://localhost:1026/ngsi-ld/v1/entities?options=keyValues
```

**Query temporal data (via Mintaka):**
```bash
curl "http://localhost:8080/ngsi-ld/v1/temporal/entities?type=Gesture&timerel=after&timeAt=2025-01-01T00:00:00Z"
```

**Subscribe to entity changes:**
```bash
curl -X POST http://localhost:1026/ngsi-ld/v1/subscriptions \
  -H "Content-Type: application/json" \
  -d '{
    "type": "Subscription",
    "entities": [{"type": "Gesture"}],
    "notification": {
      "endpoint": {"uri": "http://my-consumer:8080/notify"}
    }
  }'
```

### Data Model

Each ROS 2 topic forwarded via Integration Service is represented as an NGSI-LD entity. Example for a `Gesture`:

```json
{
  "id": "urn:ngsi-ld:Gesture:person1",
  "type": "Gesture",
  "type_field": { "type": "Property", "value": 0 },
  "payload": { "type": "Property", "value": "up" }
}
```

---

## DDS NGSI-LD Integration

### DDS Enabler Configuration (`config/orion-dds.json`)

The `orion-dds.json` file configures the **eProsima DDS Enabler**, which bridges DDS topics directly into NGSI-LD entities without going through the Integration Service:

```json
{
  "dds": {
    "ddsmodule": {
      "dds": {
        "domain": 0,
        "allowlist": [{ "name": "*" }]
      },
      "topics": {
        "name": "*",
        "qos": {
          "durability": "TRANSIENT_LOCAL",
          "history-depth": 10
        }
      },
      "specs": {
        "threads": 12,
        "logging": { "stdout": false, "verbosity": "info" }
      }
    },
    "ngsild": {
      "topics": {
        "rt/cmd_vel": {
          "entityType": "Robot",
          "entityId": "urn:ngsi-ld:robot:1",
          "attribute": "velocityCommand"
        },
        "rt/pose": {
          "entityType": "Robot",
          "entityId": "urn:ngsi-ld:robot:1",
          "attribute": "pose"
        }
      }
    }
  }
}
```

Key settings:
- `domain: 0` -- matches `ROS_DOMAIN_ID=0`
- `durability: TRANSIENT_LOCAL` -- late-joining subscribers receive the last cached value
- `history-depth: 10` -- retains the last 10 samples per topic
- `threads: 12` -- parallel processing for multi-topic throughput

### Integration Service Bridge (`config/integration_service.yaml`)

```yaml
systems:
  ros2:
    type: ros2_dynamic
  fiware:
    type: fiware
    host: 127.0.0.1
    port: 1026

routes:
  ros2_to_fiware: { from: ros2, to: fiware }

topics:
  /sunrise_app/bridge/intent:
    type: "sunrise_msgs/msg/Intent"
    route: ros2_to_fiware
  /sunrise_app/bridge/action:
    type: "sunrise_msgs/msg/Action"
    route: ros2_to_fiware
  /camera_tracking/pointing:
    type: "sunrise_msgs/msg/Marker"
    route: ros2_to_fiware
  /human/body/person1/gesture:
    type: "sunrise_msgs/msg/Gesture"
    route: ros2_to_fiware
  /human/voices/person1/livespeech:
    type: "sunrise_msgs/msg/Transcription"
    route: ros2_to_fiware
```

---

## ROS4HRI

The Sunrise middleware follows the **ROS4HRI** REP-155 convention for human-related topics. All topics related to a specific person are namespaced under `/human/`:

| ROS4HRI Topic | Sunrise Usage |
|--------------|---------------|
| `/human/body/person1/gesture` | Gesture and touch events from Tactigon-Skin |
| `/human/voices/person1/livespeech` | Real-time speech transcription |
| `/human/voice/person1/stream` | Trigger for on-device speech recognition |

The `person1` identifier is fixed in this POC. Future implementations may use dynamic person tracking (e.g., `/human/body/{person_id}/gesture`) when multiple operators are supported.

---

## `sunrise_msgs` - Message Definitions

### `Action.msg`

Represents a single input action from any modality.

```text
int8 GESTURE       = 0
int8 VOICE_COMMAND = 1
int8 TOUCH         = 2
int8 CAMERA_POINT  = 3
int8 MARKER        = 4

int8 type
string payload    # JSON-encoded action data
```

### `Intent.msg`

Represents the operator's high-level intent.

```text
int8 TEACH  = 0
int8 REPEAT = 1

int8 type
string payload    # JSON-encoded intent data (e.g. task name)
```

### `Gesture.msg`

Published by `sunrise_tactigon` and `sunrise_tactigon_mock` on ROS4HRI topics.

```text
int8 HAND  = 0   # IMU-based gesture (e.g. "up", "down", "twist")
int8 TOUCH = 1   # Capacitive touch (e.g. "SINGLE_TAP", "TWO_FINGER_TAP")

int8 type
string payload
```

### `Transcription.msg`

Published by `sunrise_tactigon` and `sunrise_tactigon_mock` on ROS4HRI topics.

```text
string text_so_far    # partial in-progress transcription
string transcription  # final recognized text
string[] path         # hotword path matched in grammar tree
float64 time          # recognition duration (seconds)
bool timeout          # true if recognition window expired
```

### `BraccioCommand.msg`

Cartesian command for the Braccio robot arm.

```text
int16 x
int16 y
int16 z
string wrist_state    # "HORIZONTAL" or "VERTICAL"
string gripper_state  # "OPEN" or "CLOSE"
```

### `BraccioJointCommand.msg`

Joint-space command for the COMAU Racer 7.

```text
comau_msgs/JointPose[] trajectory  # joint positions in radians
```

### `BraccioResponse.msg`

Result of a robot move command.

```text
bool success
string status
float32 move_time  # seconds
```

### `Marker.msg` / `MarkerList.msg`

ArUco marker positions detected by `camera_tracking`.

```text
# Marker.msg
uint32 id
Point2D p1
Point2D p2
Point2D p3
Point2D p4

# MarkerList.msg
Marker[] markers

# Point2D.msg
int32 x
int32 y
```

---

## Technologies Used

* **Python 3.12**
* **ROS 2 Jazzy** on **Ubuntu 24.04** (main middleware container)
* **ROS 2 Humble** on **Ubuntu 22.04** (COMAU driver and Integration Service containers)
* **eProsima Vulcanexus** as the ROS 2 distribution and Fast-DDS provider
* **colcon build** for ROS 2 package compilation
* **Tactigon-Skin SDK** (`tactigon_gear==5.5.2`) for wearable input management
* **FIWARE Orion-LD** for NGSI-LD context brokering
* **eProsima Integration Service** for ROS2 to FIWARE bridging
* **TimescaleDB** for time-series data persistence
* **Grafana** for real-time monitoring dashboards
* **Docker Compose** for container orchestration

---

## Software Dependencies

### Main Sunrise Container (`Dockerfile`)

Base image: `eprosima/vulcanexus:jazzy-base`

| Dependency | Version | Purpose |
|-----------|---------|---------|
| `tactigon-gear` | 5.5.2 | Tactigon-Skin BLE SDK (gesture + speech) |
| `PyQt5` | latest | GUI for `sunrise_tactigon_mock` |
| `python3-pyaudio` | system | Audio I/O for speech recognition |
| `bluetooth` / `bluez` / `libbluetooth-dev` | system | Bluetooth stack for Tactigon-Skin and Braccio |
| `libboost-all-dev` | system | C++ boost libraries |
| `python3-colcon-common-extensions` | system | ROS 2 build system |

ROS 2 packages (built from source): `comau_msgs`, `sunrise_msgs`, `camera_tracking`, `sunrise`

### COMAU Driver Container (`sunrise_robot/Dockerfile`)

Base image: `eprosima/vulcanexus:humble-base`

| Dependency | Purpose |
|-----------|---------|
| `ros-humble-ros2-controllers` | Controller framework |
| `ros-humble-ros2-control` | Hardware abstraction layer |
| `ros-humble-controller-manager` | Controller lifecycle management |
| `ros-humble-hardware-interface` | Robot hardware interface |
| `ros-humble-trajectory-msgs` | Joint trajectory messages |
| `ros-humble-xacro` | Robot description macros |
| `ros-humble-rviz2` | Visualization |

### Integration Service Container (`sunrise_fiware/Dockerfile`)

Base image: `eprosima/vulcanexus:humble-base`

| Dependency | Purpose |
|-----------|---------|
| `libyaml-cpp-dev` | YAML config parsing |
| `libcurlpp-dev` / `libcurl4-openssl-dev` | FIWARE HTTP client |
| `libwebsocketpp-dev` | WebSocket support |
| eProsima Integration Service | ROS2 to FIWARE bridging |

### Speech Socket Container (`speech/Dockerfile`)

Standalone socket server that handles DeepSpeech-based speech recognition for the Tactigon-Skin device. Uses the `deepspeech-0.9.3-models.tflite` model and a custom vocabulary scorer for the application domain.

---

## Hardware Dependencies

| Hardware | Interface | Configuration |
|----------|-----------|---------------|
| **Tactigon-Skin** wearable (right hand) | Bluetooth LE | MAC: `C0:83:2A:34:25:38`, socket: `127.0.0.1:50007` |
| **Arduino Braccio** robotic arm | Bluetooth | MAC: `E2:48:72:F0:CC:D6` |
| **COMAU Racer 7-1.4** | Ethernet (ROS 2 Action server) | Model: `racer7-14` |
| **USB/CSI Camera** | V4L2 (`/dev/video*`) | 640x480 @ 15 fps, MJPEG |
| **Host PC** | -- | Bluetooth adapter + Docker with `privileged: true` for device access |

---

## Installation and Setup

### Option A: Docker Compose (recommended)

```bash
git clone https://github.com/TactigonTeam/Tactigon-Sunrise.git
cd Tactigon-Sunrise

# Allow X11 forwarding for GUI nodes
xhost +local:docker

# Start all services
docker compose up --build
```

### Option B: Native ROS 2 Build

#### 1. Clone the repository

```bash
git clone https://github.com/TactigonTeam/Tactigon-Sunrise.git
cd Tactigon-Sunrise
```

#### 2. Install Python dependencies

```bash
pip3 install tactigon-gear==5.5.2 PyQt5 --break-system-packages
```

#### 3. Build ROS 2 packages

```bash
source /opt/vulcanexus/jazzy/setup.bash
colcon build --packages-select comau_msgs
source install/setup.bash
colcon build --packages-select sunrise_msgs
colcon build --packages-select camera_tracking
colcon build --packages-select sunrise
source install/setup.bash
```

#### 4. Run the nodes

```bash
# Input layer -- hardware
ros2 run sunrise sunrise_tactigon config/sunrise_tactigon.json
# Input layer -- hardware-free mock (for testing)
ros2 run sunrise sunrise_mock

# Interpretation layer
ros2 run sunrise sunrise_bridge config/sunrise_bridge.json

# Mission control
ros2 run sunrise mission_controller config/mission_controller.json

# Robot driver (Braccio)
ros2 run sunrise sunrise_braccio config/sunrise_braccio.json

# Robot driver (COMAU Racer 7)
ros2 run sunrise sunrise_comau config/sunrise_comau.json
```

#### 5. Start the FIWARE monitoring stack

```bash
cd sunrise_fiware
docker compose up -d
```

---

## Configuration Reference

| File | Node | Description |
|------|------|-------------|
| `config/mission_controller.json` | `mission_controller` | Topic names, QoS profiles, paths to TEO/LEO configs |
| `config/mission_controller_teacher.json` | TEO | Saved tasks and skill definitions |
| `config/mission_controller_student.json` | LEO | Robot definitions with command/response topics |
| `config/sunrise_bridge.json` | `sunrise_bridge` | Gesture/touch/voice to Intent/Action mappings |
| `config/sunrise_tactigon.json` | `sunrise_tactigon` | Tactigon-Skin BLE address, gesture model, speech grammar |
| `config/sunrise_braccio.json` | `sunrise_braccio` | Braccio BLE address, command/response topic names |
| `config/sunrise_comau.json` | `sunrise_comau` | COMAU command/response topic names |
| `config/camera_tracking.json` | `camera_tracking` | Camera and tracking topic names, ArUco dictionary |
| `config/integration_service.yaml` | Integration Service | ROS2 to FIWARE topic bridge configuration |
| `config/orion-dds.json` | DDS Enabler | NGSI-LD entity mapping, DDS domain and QoS settings |
| `config/ros2/config.json` | `sunrise_app` | Camera ROS 2 node parameters |
| `config/ros2/parameters/cfg_test.yaml` | `camera_ros` | Camera resolution, framerate, format |

---

## Extensibility

- `Action` and `Intent` messages can be extended with new `type` constants without breaking existing consumers.
- New robot backends can be added by implementing a command subscriber + response publisher following the pattern of `sunrise_braccio` or `sunrise_comau`, then registering the robot in `mission_controller_student.json`.
- Additional FIWARE topics can be added to `config/integration_service.yaml` without recompiling any ROS 2 package.
- The Tactigon speech grammar is fully configurable via `config/sunrise_tactigon.json` -- no code changes needed to add new voice commands.

## Additional Notes

* Tasks and skills are currently stored in JSON files; future implementations may include saving to a database.
* The middleware is modular and easily extendable to other multimodal input types (voice commands, camera-based object detection, custom sensors).
* All containers use `network_mode: host` to simplify DDS discovery across the deployment. For multi-machine deployments, configure static peer discovery via `FASTRTPS_DEFAULT_PROFILES_FILE`.

# 02 — Interfaces

This document covers all ROS 2 / Vulcanexus interfaces, FIWARE NGSI-LD data models, DDS Enabler configuration, and the Integration Service bridge configuration.

---

## 1. ROS 2 Message Types (`sunrise_msgs`)

All custom message types are defined in `src/sunrise_msgs/msg/`.

### `Gesture.msg`
```
int8 HAND  = 0   # IMU-based gesture (e.g. "up", "down", "twist")
int8 TOUCH = 1   # Capacitive touch (e.g. "SINGLE_TAP", "TWO_FINGER_TAP")

int8 type
string payload
```

### `Transcription.msg`
```
string text_so_far    # partial in-progress transcription
string transcription  # final recognised text
string[] path         # hotword path matched in grammar tree
float64 time          # recognition duration (seconds)
bool timeout          # true if recognition window expired
```

### `Action.msg`
```
int8 GESTURE       = 0
int8 VOICE_COMMAND = 1
int8 TOUCH         = 2
int8 CAMERA_POINT  = 3
int8 MARKER        = 4

int8 type
string payload    # JSON-encoded action data
```

### `Intent.msg`
```
int8 TEACH  = 0
int8 REPEAT = 1

int8 type
string payload    # JSON-encoded intent data (e.g. task name)
```

### `BraccioCommand.msg`
```
int16 x
int16 y
int16 z
string wrist_state    # "HORIZONTAL" or "VERTICAL"
string gripper_state  # "OPEN" or "CLOSE"
```

### `BraccioJointCommand.msg`
```
comau_msgs/JointPose[] trajectory  # joint positions in radians
```

### `BraccioResponse.msg`
```
bool success
string status
float32 move_time  # seconds
```

### `Marker.msg` / `MarkerList.msg`
```
# Point2D.msg
int32 x
int32 y

# Marker.msg
uint32 id
Point2D p1
Point2D p2
Point2D p3
Point2D p4

# MarkerList.msg
Marker[] markers
```

---

## 2. ROS 2 Node Reference

### `mission_controller`
**Entry point:** `ros2 run sunrise mission_controller config/mission_controller.json`

| Direction | Topic | Type | QoS |
|---|---|---|---|
| SUB | `/sunrise/mission_controller/intent` | `Intent` | RELIABLE, VOLATILE, KEEP_LAST(10) |
| SUB | `/sunrise/mission_controller/action` | `Action` | RELIABLE, VOLATILE, KEEP_LAST(10) |
| PUB | `/sunrise/mission_controller/log` | `rcl_interfaces/Log` | RELIABLE, VOLATILE, KEEP_LAST(10) |
| PUB | Robot command topics (from student config) | `BraccioCommand` / `BraccioJointCommand` | RELIABLE, VOLATILE, KEEP_LAST(1) |

Config: [`config/mission_controller.json`](../config/mission_controller.json)

---

### `sunrise_bridge`
**Entry point:** `ros2 run sunrise sunrise_bridge config/sunrise_bridge.json`

| Direction | Topic | Type | QoS |
|---|---|---|---|
| SUB | `/human/body/person1/gesture` | `Gesture` | BEST_EFFORT, VOLATILE, KEEP_LAST(5) |
| SUB | `/human/voices/person1/livespeech` | `Transcription` | BEST_EFFORT, VOLATILE, KEEP_LAST(5) |
| PUB | `/sunrise_app/bridge/action` | `Action` | RELIABLE, VOLATILE, KEEP_LAST(10) |
| PUB | `/sunrise_app/bridge/intent` | `Intent` | RELIABLE, VOLATILE, KEEP_LAST(10) |
| PUB | `/human/voice/person1/stream` | `std_msgs/String` | RELIABLE, VOLATILE, KEEP_LAST(1) |

Gesture-to-action mapping is configured in [`config/sunrise_bridge.json`](../config/sunrise_bridge.json):

```json
{
    "intent_topic": "/sunrise_app/bridge/intent",
    "action_topic": "/sunrise_app/bridge/action",
    "gestures": [
        { "gesture": "up",    "mapping": "teach_skill" },
        { "gesture": "down",  "mapping": "teach_skill" },
        { "gesture": "twist", "mapping": "repeat_task" }
    ],
    "touchs": [
        { "touch": "SINGLE_TAP",     "mapping": "teach_task" },
        { "touch": "TWO_FINGER_TAP", "mapping": "speech" }
    ],
    "transcriptions": [
        { "command": "run_job_one",   "mapping": "repeat_task" },
        { "command": "start_job_two", "mapping": "repeat_task" }
    ]
}
```

---

### `sunrise_tactigon`
**Entry point:** `ros2 run sunrise sunrise_tactigon config/sunrise_tactigon.json`

| Direction | Topic | Type | QoS |
|---|---|---|---|
| PUB | `/human/body/person1/gesture` | `Gesture` | BEST_EFFORT, VOLATILE, KEEP_LAST(5) |
| PUB | `/human/voices/person1/livespeech` | `Transcription` | BEST_EFFORT, VOLATILE, KEEP_LAST(5) |
| SUB | `/human/voice/person1/stream` | `std_msgs/String` | RELIABLE, VOLATILE, KEEP_LAST(1) |

---

### `sunrise_tactigon_mock` (hardware-free)
**Entry point:** `ros2 run sunrise sunrise_mock`

| Direction | Topic | Type | QoS |
|---|---|---|---|
| PUB | `/human/body/person1/gesture` | `Gesture` | BEST_EFFORT, VOLATILE, KEEP_LAST(5) |
| PUB | `/human/voices/person1/livespeech` | `Transcription` | BEST_EFFORT, VOLATILE, KEEP_LAST(5) |

---

### `sunrise_braccio`
**Entry point:** `ros2 run sunrise sunrise_braccio config/sunrise_braccio.json`

| Direction | Topic | Type | QoS |
|---|---|---|---|
| SUB | `/robot/braccio/command` | `BraccioCommand` | RELIABLE, VOLATILE, KEEP_LAST(1) |
| PUB | `robot/braccio/response` | `BraccioResponse` | RELIABLE, VOLATILE, KEEP_LAST(1) |

---

### `sunrise_comau`
**Entry point:** `ros2 run sunrise sunrise_comau config/sunrise_comau.json`

| Direction | Topic / Action | Type | QoS |
|---|---|---|---|
| SUB | `/robot/comau/action` | `BraccioJointCommand` | RELIABLE, VOLATILE, KEEP_LAST(1) |
| PUB | `/robot/comau/action_result` | `comau_msgs/ActionResult` | RELIABLE, VOLATILE, KEEP_LAST(1) |
| ACTION CLIENT | `/execute_joint_trajectory_handler` | `comau_msgs/ExecuteJointTrajectory` | ROS 2 Action |

---

### `camera_tracking`
Config: [`config/camera_tracking.json`](../config/camera_tracking.json)

| Direction | Topic | Type | QoS |
|---|---|---|---|
| SUB | `/camera/image_raw` | `sensor_msgs/Image` | BEST_EFFORT, VOLATILE, KEEP_LAST(1) |
| PUB | `/camera_tracking/image` | `sensor_msgs/Image` | BEST_EFFORT, VOLATILE, KEEP_LAST(1) |
| PUB | `/camera_tracking/markers` | `MarkerList` | RELIABLE, VOLATILE, KEEP_LAST(10) |
| PUB | `/camera_tracking/pointing` | `Marker` | RELIABLE, VOLATILE, KEEP_LAST(10) |

---

## 3. Complete Topic Reference

| Topic | Type | Publisher | Subscriber | QoS |
|---|---|---|---|---|
| `/human/body/person1/gesture` | `Gesture` | `sunrise_tactigon` / `_mock` | `sunrise_bridge` | BEST_EFFORT, KEEP_LAST(5) |
| `/human/voices/person1/livespeech` | `Transcription` | `sunrise_tactigon` / `_mock` | `sunrise_bridge` | BEST_EFFORT, KEEP_LAST(5) |
| `/human/voice/person1/stream` | `std_msgs/String` | `sunrise_bridge` | `sunrise_tactigon` | RELIABLE, KEEP_LAST(1) |
| `/sunrise_app/bridge/action` | `Action` | `sunrise_bridge` | `mission_controller`, Integration Service | RELIABLE, KEEP_LAST(10) |
| `/sunrise_app/bridge/intent` | `Intent` | `sunrise_bridge` | `mission_controller`, Integration Service | RELIABLE, KEEP_LAST(10) |
| `/sunrise/mission_controller/log` | `rcl_interfaces/Log` | `mission_controller` | Integration Service | RELIABLE, KEEP_LAST(10) |
| `/robot/braccio/command` | `BraccioCommand` | `mission_controller` (LEO) | `sunrise_braccio` | RELIABLE, KEEP_LAST(1) |
| `robot/braccio/response` | `BraccioResponse` | `sunrise_braccio` | `mission_controller` | RELIABLE, KEEP_LAST(1) |
| `/robot/comau/action` | `BraccioJointCommand` | `mission_controller` (LEO) | `sunrise_comau` | RELIABLE, KEEP_LAST(1) |
| `/robot/comau/action_result` | `comau_msgs/ActionResult` | `sunrise_comau` | `mission_controller` | RELIABLE, KEEP_LAST(1) |
| `/execute_joint_trajectory_handler` | `ExecuteJointTrajectory` | `sunrise_robot` | `sunrise_comau` | ROS 2 Action |
| `/camera/image_raw` | `sensor_msgs/Image` | Camera driver | `camera_tracking` | BEST_EFFORT, KEEP_LAST(1) |
| `/camera_tracking/markers` | `MarkerList` | `camera_tracking` | `mission_controller` | RELIABLE, KEEP_LAST(10) |
| `/camera_tracking/pointing` | `Marker` | `camera_tracking` | Integration Service | RELIABLE, KEEP_LAST(10) |

---

## 4. FIWARE NGSI-LD Interfaces

### 4.1 Integration Service Configuration

[`config/integration_service.yaml`](../config/integration_service.yaml) bridges ROS 2 topics to FIWARE Orion-LD:

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

### 4.2 NGSI-LD Data Models

Each forwarded topic becomes an NGSI-LD entity. Below are example payloads.

#### Gesture entity
```json
{
  "id": "urn:ngsi-ld:Gesture:person1",
  "type": "Gesture",
  "@context": "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
  "gestureType": {
    "type": "Property",
    "value": 0
  },
  "payload": {
    "type": "Property",
    "value": "twist"
  }
}
```

#### Action entity
```json
{
  "id": "urn:ngsi-ld:Action:bridge",
  "type": "Action",
  "@context": "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
  "actionType": {
    "type": "Property",
    "value": 0
  },
  "payload": {
    "type": "Property",
    "value": "{\"task\": \"repeat_task\"}"
  }
}
```

#### Intent entity
```json
{
  "id": "urn:ngsi-ld:Intent:bridge",
  "type": "Intent",
  "@context": "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
  "intentType": {
    "type": "Property",
    "value": 1
  },
  "payload": {
    "type": "Property",
    "value": "{\"task_name\": \"solder_1\"}"
  }
}
```

#### Transcription entity
```json
{
  "id": "urn:ngsi-ld:Transcription:person1",
  "type": "Transcription",
  "@context": "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
  "textSoFar": {
    "type": "Property",
    "value": "run job"
  },
  "transcription": {
    "type": "Property",
    "value": "run job one"
  },
  "path": {
    "type": "Property",
    "value": ["start", "job", "one"]
  },
  "timeout": {
    "type": "Property",
    "value": false
  }
}
```

#### Marker (ArUco pointing) entity
```json
{
  "id": "urn:ngsi-ld:Marker:camera1",
  "type": "Marker",
  "@context": "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
  "markerId": {
    "type": "Property",
    "value": 42
  },
  "p1": {
    "type": "Property",
    "value": { "x": 320, "y": 240 }
  }
}
```

#### Generic module status entity
```json
{
  "id": "urn:ngsi-ld:ReusableModule:sunrise",
  "type": "SunriseModule",
  "@context": "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
  "status": {
    "type": "Property",
    "value": "running"
  },
  "activeNode": {
    "type": "Property",
    "value": "mission_controller"
  },
  "controllerState": {
    "type": "Property",
    "value": "IDLE"
  }
}
```

### 4.3 NGSI-LD API Usage

```bash
# Query all entities
curl http://localhost:1026/ngsi-ld/v1/entities?options=keyValues

# Query temporal gesture data (via Mintaka)
curl "http://localhost:8080/ngsi-ld/v1/temporal/entities?type=Gesture&timerel=after&timeAt=2025-01-01T00:00:00Z"

# Subscribe to entity changes
curl -X POST http://localhost:1026/ngsi-ld/v1/subscriptions \
  -H "Content-Type: application/json" \
  -d '{
    "type": "Subscription",
    "entities": [{ "type": "Gesture" }],
    "notification": {
      "endpoint": { "uri": "http://your-endpoint/notify" }
    }
  }'
```

---

## 5. DDS Enabler Configuration

[`config/orion-dds.json`](../config/orion-dds.json) configures the **eProsima DDS Enabler** to bridge DDS topics directly into NGSI-LD entities:

```json
{
  "dds": {
    "ddsmodule": {
      "dds": {
        "domain": 0,
        "allowlist": [{ "name": "*" }],
        "blocklist": [{ "name": "add_blocked_topics_list_here" }]
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
        "logging": {
          "stdout": false,
          "verbosity": "info"
        }
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

**Key settings:**
- `domain: 0` — matches `ROS_DOMAIN_ID=0` across all containers
- `durability: TRANSIENT_LOCAL` — late-joining subscribers receive last cached value
- `history-depth: 10` — retains last 10 samples per topic
- `threads: 12` — parallel processing for multi-topic throughput

> **[TODO]** Add per-topic NGSI-LD entity mappings for Sunrise topics (`/sunrise_app/bridge/intent`, `/human/body/person1/gesture`, etc.) in `config/orion-dds.json` to enable direct DDS Enabler → Orion-LD bridging without the Integration Service.

---

## 6. Telemetry Topics

Telemetry topics are consumed directly by `ros_to_db_bridge.py` and written to the `telemetria_robot` TimescaleDB table:

| Topic | Type | Description |
|---|---|---|
| `/sunrise/telemetry/setup_time` | `std_msgs/Float64` | Time to complete robot setup (seconds) |
| `/sunrise/telemetry/job_success_rate` | `std_msgs/Float64` | Ratio of successful job executions |
| `/sunrise/telemetry/retries` | `std_msgs/Float64` | Number of retries in last execution |
| `/sunrise/telemetry/downtime` | `std_msgs/Float64` | Total downtime (seconds) |
| `/sunrise/telemetry/time_to_recall_db` | `std_msgs/Float64` | DB query latency |

---

## 7. Runtime Environment

| Container | ROS 2 Version | Base Image |
|---|---|---|
| `sunrise` (main) | Jazzy (Ubuntu 24.04) | `eprosima/vulcanexus:jazzy-base` |
| `sunrise-comau` (COMAU driver) | Humble (Ubuntu 22.04) | `eprosima/vulcanexus:humble-base` |
| `integration-service` | Humble | `eprosima/vulcanexus:humble-base` |

All containers use `network_mode: host` with `ROS_DOMAIN_ID=0` for transparent cross-version DDS discovery.

| Variable | Value | Description |
|---|---|---|
| `ROS_DOMAIN_ID` | `0` | All nodes in the same DDS domain |
| `RMW_IMPLEMENTATION` | `rmw_fastrtps_cpp` | Fast-DDS RMW (default in Vulcanexus) |
| `ROBOT_MODEL` | `racer7-14` | COMAU robot model identifier |

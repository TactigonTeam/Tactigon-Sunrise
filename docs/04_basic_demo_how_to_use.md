# 04 — Basic Demo: How to Use

This document describes the complete teach-and-repeat demo scenario, all commands, expected outputs, and how to monitor the system in Grafana. It runs **entirely without hardware** using `sunrise_tactigon_mock`.

---

## 1. Scenario

An operator uses the mock wearable GUI to:

1. **Teach** two robot movements (skills) and save them as a task.
2. **Replay** the saved task on command.
3. **Monitor** all interaction events in real-time via FIWARE / Grafana.

This mirrors the real production scenario at Plastifer where an operator teaches the COMAU Racer 7 soldering positions and recalls them for each product variant.

---

## 2. Prerequisites

Stack is running (from [03_installation_and_hello_world.md](03_installation_and_hello_world.md)):

```bash
# Terminal 1
ros2 run sunrise mission_controller config/mission_controller.json

# Terminal 2
ros2 run sunrise sunrise_bridge config/sunrise_bridge.json

# Terminal 3
ros2 run sunrise sunrise_mock
```

Optional — FIWARE monitoring stack:
```bash
cd sunrise_fiware
docker compose up -d
# Navigate to http://localhost:3000 (admin/admin)
```

---

## 3. Phase 1 — Enter Teach Mode

### Command
In the mock GUI:
- **Type:** `TOUCH`
- **Payload:** `SINGLE_TAP`
- Click **Send Gesture**

### Bridge mapping (`config/sunrise_bridge.json`)
```json
{ "touch": "SINGLE_TAP", "mapping": "teach_task" }
```

### Expected output

**Terminal 2 (bridge):**
```
[sunrise_bridge]: Touch received: SINGLE_TAP
[sunrise_bridge]: Mapping: teach_task
[sunrise_bridge]: Publishing Action type=TOUCH payload={"action": "teach_task"}
```

**Terminal 1 (mission_controller):**
```
[mission_controller]: Action received: teach_task
[mission_controller]: State transition: IDLE → TEACH
[mission_controller]: TEO active. Waiting for skills...
```

---

## 4. Phase 2 — Record Skill 1 (gesture `up`)

### Command
In the mock GUI:
- **Type:** `HAND`
- **Payload:** `up`
- Click **Send Gesture**

### Bridge mapping
```json
{ "gesture": "up", "mapping": "teach_skill" }
```

### Expected output

**Terminal 2 (bridge):**
```
[sunrise_bridge]: Gesture received: type=HAND payload=up
[sunrise_bridge]: Mapping: teach_skill
[sunrise_bridge]: Publishing Action type=GESTURE payload={"action": "teach_skill", "gesture": "up"}
```

**Terminal 1 (mission_controller):**
```
[mission_controller]: Skill 1 recorded: gesture=up
```

---

## 5. Phase 3 — Record Skill 2 (gesture `down`)

### Command
In the mock GUI:
- **Type:** `HAND`
- **Payload:** `down`
- Click **Send Gesture**

### Expected output

**Terminal 1 (mission_controller):**
```
[mission_controller]: Skill 2 recorded: gesture=down
```

---

## 6. Phase 4 — Save Task (end teach mode)

### Command
In the mock GUI:
- **Type:** `TOUCH`
- **Payload:** `SINGLE_TAP`
- Click **Send Gesture**

### Expected output

**Terminal 1 (mission_controller):**
```
[mission_controller]: Task saved to config/mission_controller_teacher.json
[mission_controller]: State transition: TEACH → IDLE
[mission_controller]: TEO deactivated.
```

You can verify the saved task:
```bash
cat config/mission_controller_teacher.json
```

Example content:
```json
{
  "tasks": [
    {
      "name": "task_001",
      "skills": [
        { "gesture": "up" },
        { "gesture": "down" }
      ]
    }
  ]
}
```

---

## 7. Phase 5 — Replay the Task (gesture `twist`)

### Command
In the mock GUI:
- **Type:** `HAND`
- **Payload:** `twist`
- Click **Send Gesture**

### Bridge mapping
```json
{ "gesture": "twist", "mapping": "repeat_task" }
```

### Expected output

**Terminal 2 (bridge):**
```
[sunrise_bridge]: Gesture received: type=HAND payload=twist
[sunrise_bridge]: Mapping: repeat_task
[sunrise_bridge]: Publishing Intent type=REPEAT payload={"task_name": "task_001"}
```

**Terminal 1 (mission_controller):**
```
[mission_controller]: Intent received: type=REPEAT task=task_001
[mission_controller]: State transition: IDLE → REPEAT
[mission_controller]: LEO active. Replaying task_001...
[mission_controller]: Publishing robot command skill 1: gesture=up
[mission_controller]: Publishing robot command skill 2: gesture=down
[mission_controller]: State transition: REPEAT → IDLE
```

### Verify robot command topics

```bash
# Braccio command (pick-and-place demo)
ros2 topic echo /robot/braccio/command

# COMAU joint command (industrial arm demo)
ros2 topic echo /robot/comau/action
```

Sample Braccio command output:
```yaml
x: 100
y: 100
z: 100
wrist_state: HORIZONTAL
gripper_state: OPEN
---
```

---

## 8. Phase 6 — Replay via Voice Command

Alternatively, replay the task using a voice transcription:

In the mock GUI (Transcription section):
- **Transcription:** `run job one`
- Click **Send Transcription**

### Bridge mapping
```json
{ "command": "run_job_one", "mapping": "repeat_task" }
```

### Expected output — same as Phase 5.

---

## 9. Monitoring in FIWARE / Grafana

### 9.1 Start the monitoring stack

```bash
cd sunrise_fiware
docker compose up -d
```

Open **http://localhost:3000** (credentials: `admin` / `admin`).

Navigate to **Dashboards → Sunrise** to see live panels for:
- Gesture events timeline
- Intent / Action stream
- Telemetry KPIs (setup time, job success rate, retries, downtime)

### 9.2 Query entities via NGSI-LD API

```bash
# List all entities
curl http://localhost:1026/ngsi-ld/v1/entities?options=keyValues

# Get latest Gesture entity
curl http://localhost:1026/ngsi-ld/v1/entities/urn:ngsi-ld:Gesture:person1?options=keyValues

# Get temporal Gesture history (via Mintaka)
curl "http://localhost:8080/ngsi-ld/v1/temporal/entities?type=Gesture&timerel=after&timeAt=2025-01-01T00:00:00Z"
```

### 9.3 Sample Orion-LD response after a gesture event

```json
{
  "id": "urn:ngsi-ld:Gesture:person1",
  "type": "Gesture",
  "gestureType": { "type": "Property", "value": 0 },
  "payload": { "type": "Property", "value": "twist" }
}
```

---

## 10. Advanced Demo — COMAU Joint Trajectory

If a `sunrise-comau` container is running with COMAU hardware available, the mission controller reads the joint trajectory from [`config/mission_controller_teacher.json`](../config/mission_controller_teacher.json):

```json
{
  "tasks": [{
    "name": "solder_1",
    "skills": [{
      "scope": "comau_robot",
      "name": "move",
      "payload": {
        "trajectory": [
          { "positions": [0.39, 0.270, -0.97, 0.0, 0.89, 0.0, 0.0, 0.0, 0.0] },
          { "positions": [0.78, 0.52, -0.12, 0.0, 1.39, 0.0, 0.0, 0.0, 0.0] }
        ]
      }
    }]
  }]
}
```

Monitor COMAU command topic:
```bash
ros2 topic echo /robot/comau/action
```

---

## 11. Complete Interaction Reference

### Gesture commands

| Mock GUI Input | Bridge Mapping | Mission Controller Action |
|---|---|---|
| `TOUCH` / `SINGLE_TAP` | `teach_task` | Enter TEACH mode (TEO activated) |
| `HAND` / `up` | `teach_skill` | Record skill (`up` gesture) |
| `HAND` / `down` | `teach_skill` | Record skill (`down` gesture) |
| `TOUCH` / `SINGLE_TAP` (in TEACH) | `teach_task` | Save task → return to IDLE |
| `HAND` / `twist` | `repeat_task` | Replay last saved task (LEO activated) |
| `TOUCH` / `TWO_FINGER_TAP` | `speech` | Activate voice command mode |

### Voice commands

| Transcription | Bridge Mapping | Mission Controller Action |
|---|---|---|
| `run job one` | `repeat_task` | Replay saved task |
| `start job two` | `repeat_task` | Replay saved task |

---

## 12. Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| Mock GUI does not open | No X11 forwarding | Run `xhost +local:docker` before starting the container |
| `ros2 run sunrise sunrise_mock` fails | `install/setup.bash` not sourced | `source install/setup.bash` |
| No output in mission_controller | `sunrise_bridge` not running | Start bridge first (Terminal 2) |
| FIWARE entities not appearing | Integration Service not running | `cd sunrise_fiware && docker compose up -d` |
| `command not found: ros2` | ROS 2 environment not sourced | `source /opt/vulcanexus/jazzy/setup.bash` |

---
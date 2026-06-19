# 05 — Role in the TRL 6-7 Demonstrator

This document describes how the Sunrise middleware was deployed in the TRL 6-7 industrial demonstrator at **Plastifer** (Brescia, Italy), the impact results achieved, and the relationship between the open repository and the production system.

---

## 1. Demonstrator Context

**End user:** Plastifer s.r.l. — an SME producing highly customised sinks and ventilators in Brescia, Italy.

**Problem:** Each product variant requires frequent robot reprogramming. Traditional programming requires expert-level knowledge of robot-specific languages and tooling, which creates a bottleneck on the production floor.

**Demonstrator goal:** Validate that a non-programmer operator can program and supervise a robotic soldering workstation using only natural voice and gesture commands — without writing any code.

---

## 2. Demonstrator Architecture

```
+--------------------------------------------------------------------------+
|                       Industrial Workstation — Plastifer                  |
|                                                                           |
|  Operator (Tactigon-Skin)                                                 |
|       │ gesture + touch + voice                                           |
|       ▼                                                                   |
|  sunrise_tactigon ──────────────────────────────────────────────────►    |
|  /human/body/person1/gesture                                              |
|  /human/voices/person1/livespeech                                         |
|       │                                                                   |
|       ▼                                                                   |
|  sunrise_bridge (Intent Router)                                            |
|       │  /sunrise/mission_controller/action                               |
|       │  /sunrise/mission_controller/intent                               |
|       ▼                                                                   |
|  mission_controller (TEO + LEO)                                            |
|       │  /robot/comau/action (BraccioJointCommand)                        |
|       ▼                                                                   |
|  sunrise_comau ────► ExecuteJointTrajectory ────► COMAU Racer 7-1.4       |
|                                                                           |
|  camera_tracking ──► /camera_tracking/pointing ──► ArUco target selection|
|                                                                           |
|  Integration Service ──► FIWARE Orion-LD ──► TimescaleDB ──► Grafana      |
+--------------------------------------------------------------------------+
```

---

## 3. Deployment Setup

### Hardware

| Component | Model | Interface |
|---|---|---|
| Wearable | Tactigon-Skin (right-hand) | Bluetooth LE · MAC `C0:83:2A:34:25:38` |
| Industrial arm | COMAU Racer 7-1.4 | Ethernet · ROS 2 Action |
| Camera | USB camera 640×480 @ 15 fps MJPEG | V4L2 `/dev/video*` |
| Host PC | — | Bluetooth adapter + Docker |

### Software Containers Running in Production

| Container | Image | Role |
|---|---|---|
| `sunrise` | `eprosima/vulcanexus:jazzy-base` (custom) | All Sunrise ROS 2 nodes |
| `tactigon-speech-socket` | `speech/Dockerfile` | DeepSpeech ASR socket |
| `sunrise-comau` | `eprosima/vulcanexus:humble-base` (custom) | COMAU driver (Humble) |
| `integration-service` | `sunrise_fiware/Dockerfile` | ROS 2 → FIWARE bridge |
| `fiware-orion` | `fiware/orion-ld:latest` | NGSI-LD Context Broker |
| `sunrise-timescaledb` | `timescale/timescaledb:latest-pg17` | Telemetry + TRoE storage |
| `sunrise-grafana` | `grafana/grafana:latest` | Live dashboard |

### Nodes Running Inside `sunrise` Container

```
mission_controller   — config/mission_controller.json
sunrise_bridge       — config/sunrise_bridge.json
sunrise_tactigon     — config/sunrise_tactigon.json
camera_tracking      — config/camera_tracking.json
sunrise_comau        — config/sunrise_comau.json
```

---

## 4. Operator Workflow in Production

### 4.1 Teaching Phase

1. Operator wears Tactigon-Skin and approaches the workstation.
2. Double-tap on wrist → TEO enters **TEACH** mode.
3. Operator moves to the first soldering position and gestures `up` → Skill 1 recorded.
4. Operator moves to the return position and gestures `down` → Skill 2 recorded.
5. Single-tap → Task saved to `config/mission_controller_teacher.json`.
6. Voice feedback (via system speaker): *"Task saved."*

### 4.2 ArUco Marker Pointing

For position-based job creation:
1. Operator points an ArUco marker held in hand toward the workspace target.
2. `camera_tracking` node detects the marker and publishes the centroid on `/camera_tracking/pointing`.
3. `sunrise_bridge` converts the marker event to a `CAMERA_POINT` action → `ADD_POSITION` intent.
4. `mission_controller` stores the position ID.

### 4.3 Recall and Execution Phase

1. Operator says *"run job one"* or gestures `twist`.
2. `sunrise_tactigon` publishes the transcription / gesture.
3. `sunrise_bridge` maps it to a `REPEAT` intent with task name.
4. `mission_controller` reads the joint trajectory from `config/mission_controller_teacher.json`.
5. `sunrise_comau` sends `ExecuteJointTrajectory` action to the COMAU driver.
6. COMAU Racer 7 executes the soldering motion.

### 4.4 Real-Time Monitoring

All events are streamed to FIWARE Orion-LD via the Integration Service:
- `/sunrise_app/bridge/intent` → `urn:ngsi-ld:Intent:bridge`
- `/sunrise_app/bridge/action` → `urn:ngsi-ld:Action:bridge`
- `/human/body/person1/gesture` → `urn:ngsi-ld:Gesture:person1`
- `/human/voices/person1/livespeech` → `urn:ngsi-ld:Transcription:person1`
- `/camera_tracking/pointing` → `urn:ngsi-ld:Marker:camera1`

Telemetry KPIs written to TimescaleDB via `ros_to_db_bridge.py`:
- `/sunrise/telemetry/setup_time`
- `/sunrise/telemetry/job_success_rate`
- `/sunrise/telemetry/retries`
- `/sunrise/telemetry/downtime`

---

## 5. Impact Results

| KPI | Baseline (before Sunrise) | Demonstrator Result | Improvement |
|---|---|---|---|
| Robot setup time | ~60 min (manual programming) | ~30 min (voice + gesture teach) | **−50%** |
| Job recall accuracy | N/A | **>85%** in controlled tests | — |
| Operator acceptance | Low (coding required) | High — operators preferred voice/gesture | — |
| Speech recognition accuracy (65 dB) | — | ≥85% | — |
| Speech recognition accuracy (80 dB) | — | ≥70% | — |

Non-programmer operators at Plastifer were able to program and supervise the robotic workstation independently after minimal training.

---

## 6. Open Repository vs. Production System

| Component | Open Repository | Production System |
|---|---|---|
| `sunrise_bridge` | ✅ Full source | ✅ Identical |
| `mission_controller` (TEO + LEO) | ✅ Full source | ✅ Identical |
| `sunrise_tactigon_mock` | ✅ Full source | N/A (not used in production) |
| `sunrise_comau` | ✅ Full source | ✅ Identical |
| `sunrise_braccio` | ✅ Full source | ✅ Identical |
| `camera_tracking` | ✅ Full source | ✅ Identical |
| FIWARE Integration Service config | ✅ Full config | ✅ Identical |
| Gesture ML model (`MODEL_01_R`) | ✅ Binary included | ✅ Same model |
| `sunrise_tactigon` (BLE driver) | ✅ Full source | ✅ Identical |
| Tactigon-Skin hardware | ❌ Not in repo | ✅ Physical device required |
| COMAU Racer 7 hardware | ❌ Not in repo | ✅ Physical device required |
| Custom DeepSpeech scorer (`sunrise.scorer`) | ✅ Binary included | ✅ Same file |
| Production joint trajectories | ✅ Example in `mission_controller_teacher.json` | Overwritten at teach time |

**What differs in production vs. the open repository:**
- The `config/sunrise_tactigon.json` Bluetooth address (`C0:83:2A:34:25:38`) is device-specific and must be updated for other Tactigon-Skin units.
- The joint trajectory in `config/mission_controller_teacher.json` reflects a real Plastifer soldering path and is overwritten each time the operator teaches a new task.
- The speech grammar in `config/sunrise_tactigon.json` was tuned for the Plastifer vocabulary (`run_job_one`, `start_job_two`).

---

## 7. Ad-Hoc, Proprietary, and Future Work

### Ad-Hoc (demonstrator-specific, not generalisable as-is)

- Joint trajectory waypoints in `config/mission_controller_teacher.json` are specific to the Plastifer workbench geometry.
- Speech hotword vocabulary (`config/sunrise_tactigon.json`) is tuned to Plastifer product names.
- Bluetooth device MACs for Tactigon-Skin and Arduino Braccio are hardcoded.

### Proprietary / Not Included

- Production gesture recognition model is included as a binary; source training data and re-training pipeline are proprietary to Next Industries.
- Tactigon-Skin hardware: available commercially from Next Industries.
- COMAU Racer 7 driver: requires Vulcanexus Humble licence and COMAU hardware.

### Known Limitations

- `person_id` hardcoded as `person1`; no multi-operator support.
- No automatic BLE reconnect on connection drop.
- ArUco tracking validated only at ≤2 m distance in controlled lighting.
- Task/skill catalog stored as flat JSON; no versioning or conflict resolution.

### Future Work

- Dynamic person identity and multi-operator support.
- Open-domain ASR integration (replace DeepSpeech with Whisper or similar).
- Database-backed task catalog with versioning.
- Federated learning for gesture model personalisation per operator.
- REP-155 compliant gesture message type (once standardised in `body_msgs`).
- Automatic BLE reconnect with exponential backoff.

---

## 8. Video Evidence

- In lab demo: https://drive.google.com/file/d/1ghxa9bC2_yFj3-X-cowh0cd7PctosxzU/view?usp=sharing

Architecture diagram:

![Sunrise Architecture](img/sunrise_architecture.jpg)

---

## 9. Change Log

| Version | Date | Notes |
|---|---|---|
| `0.0.1` | 2025-09 | Initial PoC release — Arduino Braccio + mock path |
| `0.0.1` | 2025-11 | TRL 6-7 demonstrator — COMAU Racer 7, Plastifer pilot |

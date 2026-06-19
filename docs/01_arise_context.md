# 01 — ARISE Context

**ARISE Project:** [arise-middleware.eu](https://arise-middleware.eu/)  
**FSTP Experiment:** SUNRISE — Smart Unified Network for Robotic Industrial Sunrise Environments  
**Company:** Next Industries s.r.l. · End-User: Plastifer s.r.l.

---

## 1. What Problem Sunrise Solves

Programming industrial robots traditionally requires expert-level knowledge of robot-specific languages and tooling. This creates a barrier on the shop floor when non-expert operators need to adapt robot behaviour for each product variant.

**Sunrise** removes that barrier. It is a software middleware layer that:

- Receives **multimodal operator inputs** — hand gestures (Tactigon-Skin wearable IMU), capacitive touch, voice commands, and ArUco marker pointing.
- Normalises all inputs into structured ROS 2 messages.
- Routes them through a **Mission Controller** (`TEO` for teaching, `LEO` for replay) managing an `IDLE → TEACH → REPEAT` state machine.
- Dispatches **robot commands** to the appropriate backend driver (Arduino Braccio over Bluetooth, COMAU Racer 7 over Ethernet).
- Streams telemetry and interaction events to **FIWARE Orion-LD** for real-time Grafana monitoring.

---

## 2. ARISE Alignment

Sunrise is a **Full-Stack Technology Provider (FSTP)** experiment within ARISE:

| ARISE Concept | Sunrise Implementation |
|---|---|
| **ARISE Middleware** | Sunrise acts as the HRI layer between human operators and industrial robots |
| **ROS 2 / Vulcanexus** | All nodes built on eProsima Vulcanexus (Fast-DDS); cross-version bridging Jazzy ↔ Humble |
| **FIWARE NGSI-LD** | Interaction events and telemetry forwarded to Orion-LD via eProsima Integration Service |
| **DDS Enabler** | `config/orion-dds.json` configures eProsima DDS Enabler for topic-to-entity mapping |
| **ROS4HRI (REP-155)** | Human topics namespaced under `/human/body/...`, `/human/voices/...` |

---

## 3. Target Robotic Platforms

| Platform | Type | Interface |
|---|---|---|
| **COMAU Racer 7-1.4** | 6-DoF collaborative industrial arm | ROS 2 Action (`ExecuteJointTrajectory`) over Ethernet |
| **Arduino Braccio** | 5-DoF desktop robotic arm | Bluetooth LE via `tactigon_arduino_braccio` |

The middleware is robot-agnostic at the command level. Any robot backend implementing the `BraccioCommand` / `BraccioJointCommand` subscriber pattern can be integrated via `config/mission_controller_student.json`.

---

## 4. Robot Missions

| Mission | Description |
|---|---|
| **Teach-and-Repeat** | Operator demonstrates a skill; system records and replays the sequence on demand |
| **Position-based Job Creation** | Operator teaches reference positions (stock pile, CNC machine, workbench) and assembles them into reusable multi-step job sequences via voice |
| **Product-driven Job Execution** | Operator recalls a previously created job (e.g., "Run Job 125B") and the system autonomously executes the full pick-and-place cycle |

---

## 5. Robot Tasks

| Task | Trigger Modality |
|---|---|
| Record a single robot movement (skill) | Gesture (`up` / `down`) or voice |
| Save task and end skill recording | Capacitive touch (`SINGLE_TAP`) |
| Replay a full saved task | Gesture (`twist`) or voice (`run_job_one`) |
| Point to a workspace target via ArUco marker | Camera + ArUco tracking |
| Activate voice command mode | Capacitive touch (`TWO_FINGER_TAP`) |
| Save a named reference position | Gesture + voice (`ADD_POSITION` intent) |
| Create a multi-step job sequence | Voice (`ADD_JOB` intent) |
| Recall and execute a specific job | Voice (`RECALL_JOB` intent) |
| Pause / resume / abort a running job | Voice command |
| Query system status | Voice command |

---

## 6. Off-the-Shelf Capabilities

| Capability | Node | Reuse Condition |
|---|---|---|
| **Gesture-to-ROS 2 bridge** | `sunrise_tactigon` | Requires Tactigon-Skin hardware + BLE adapter |
| **Voice-to-ROS 2 bridge** | `sunrise_tactigon` | Requires DeepSpeech socket container |
| **Mock wearable input GUI** | `sunrise_tactigon_mock` | No hardware — PyQt5 only |
| **Semantic intent router** | `sunrise_bridge` | Consumes any `Gesture` + `Transcription` publisher |
| **Teach-and-repeat mission controller** | `mission_controller` (TEO + LEO) | Pure ROS 2; robot-agnostic |
| **COMAU Racer 7 ROS 2 driver** | `sunrise_comau` + `sunrise_robot` | COMAU hardware / Vulcanexus Humble |
| **Arduino Braccio BLE driver** | `sunrise_braccio` | Braccio hardware + BLE adapter |
| **ArUco marker tracking** | `camera_tracking` | USB camera + `sensor_msgs/Image` source |
| **FIWARE real-time monitoring** | `sunrise_fiware` | Docker Compose stack |

---

## 7. ROS4HRI Alignment

Sunrise follows **ROS4HRI REP-155** for human-related topics.

| ROS4HRI Concept | Sunrise Topic | Message Type | Notes |
|---|---|---|---|
| Body / gesture | `/human/body/person1/gesture` | `sunrise_msgs/Gesture` | IMU-based (`HAND`) and capacitive (`TOUCH`) events |
| Voice / live speech | `/human/voices/person1/livespeech` | `sunrise_msgs/Transcription` | Partial + final recognised text, hotword path |
| Voice stream trigger | `/human/voice/person1/stream` | `std_msgs/String` | Triggers on-device ASR |

**Deviations from REP-155:**

- `person_id` is hardcoded as `person1`; dynamic multi-person tracking is not yet supported.
- `sunrise_msgs/Gesture` is a custom message type; standard `body_msgs` gesture type does not yet exist in REP-155.
- ROS4HRI `BodyParts` / skeleton tracking is not used; gestures derive from wrist IMU data.
- No `sunrise_hri_msgs` extension package is published separately; message types live in `sunrise_msgs`.

**Human-centric concepts produced by Sunrise:**

| Concept | Source | Topic |
|---|---|---|
| Human presence / identity | Hardcoded `person1` | `/human/body/person1/gesture` |
| Gesture event (`HAND` type) | Tactigon-Skin IMU + ML model | `/human/body/person1/gesture` |
| Touch event (`TOUCH` type) | Tactigon-Skin capacitive pad | `/human/body/person1/gesture` |
| Speech intent (partial) | DeepSpeech socket | `/human/voices/person1/livespeech` |
| Speech intent (final) | DeepSpeech socket | `/human/voices/person1/livespeech` |
| Pointing / workspace target | ArUco marker + camera | `/camera_tracking/pointing` |
| Operator action | `sunrise_bridge` fusion | `/sunrise/mission_controller/action` |
| Operator intent | `sunrise_bridge` fusion | `/sunrise/mission_controller/intent` |

---

## 8. Open vs. Proprietary Boundary

| Component | Status | Notes |
|---|---|---|
| ROS 2 middleware nodes (`sunrise_bridge`, `mission_controller`, `sunrise_braccio`, `sunrise_comau`, `sunrise_tactigon_mock`) | **Open** | Apache 2.0 |
| `sunrise_msgs`, `camera_tracking`, `comau_msgs` ROS 2 packages | **Open** | Apache 2.0 |
| FIWARE Integration Service configuration (`config/integration_service.yaml`) | **Open** | Apache 2.0 |
| Docker Compose stack | **Open** | Apache 2.0 |
| Gesture recognition ML model (`data/models/MODEL_01_R/model.pickle`) | **Proprietary** | Trained on right-hand Tactigon-Skin; mock node present for demo and debug purpose |
| Voice command recognition | **Proprietary** | Trained on English language, with specific keywords; mock node present for demo and debug purpose |
| Tactigon-Skin BLE hardware | **Proprietary hardware** | Requires physical device; mock node present for demo and debug purpose |
| Arduino Braccio BLE hardware | **Proprietary hardware** | replaceable with any ROS 2 subscriber |
| COMAU Racer 7 robot driver | **Conditional** | Requires COMAU hardware + Vulcanexus Humble licence |

**Hardware-free path:** Use `sunrise_tactigon_mock` (PyQt5 GUI) to emulate all wearable inputs. No Tactigon-Skin, no Braccio, no COMAU, and no camera are required for integration testing.

---

## 9. Known Limitations

| Area | Limitation |
|---|---|
| Multi-operator | `person_id` is hardcoded as `person1`; only one operator at a time |
| Gesture model | Pre-trained model is specific to right-hand Tactigon-Skin; re-training required for other devices |
| Speech grammar | Limited to domain-specific hotwords in `config/sunrise_tactigon.json`; no open-domain ASR |
| Task persistence | Skills and tasks are stored as JSON files; no database-backed versioning |
| COMAU driver | Cross-version DDS discovery requires `network_mode: host` on the same machine |
| Camera tracking | ArUco detection sensitive to lighting and marker size; no depth estimation |
| FIWARE entity IDs | Static entity IDs (e.g., `urn:ngsi-ld:Gesture:person1`); multi-instance requires ID namespacing |
| BLE reliability | Automatic reconnect not implemented |
| Noisy environments | ASR accuracy degrades at ≥80 dB; multimodal gesture fallback recommended |

---

## 10. Maintainer / Contact

| | |
|---|---|
| **Company** | Next Industries s.r.l. |
| **Authors** | Massimiliano Bellino · Stefano Barbareschi |
| **Email** | massimiliano.bellino@nextind.eu · developer@nextind.eu |
| **License** | Apache 2.0 |
| **ARISE page** | [arise-middleware.eu](https://arise-middleware.eu/) |

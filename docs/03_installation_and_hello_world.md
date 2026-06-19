# 03 — Installation & Hello World

This document covers installation (Docker and native), all software and hardware dependencies, and a verified Hello World path that runs **without any hardware**.

---

## 1. Prerequisites

| Requirement | Minimum Version | Notes |
|---|---|---|
| Docker | ≥ 24 | Rootless or root |
| Docker Compose V2 | ≥ 2.20 | `docker compose` (not `docker-compose`) |
| X11 server | any | Required for PyQt5 mock GUI and RViz |
| Bluetooth adapter | any | Only for Tactigon-Skin / Arduino Braccio |

---

## 2. Option A — Docker Compose (Recommended)

### 2.1 Clone and allow X11 forwarding

```bash
git clone https://github.com/TactigonTeam/Tactigon-Sunrise.git
cd Tactigon-Sunrise

# Allow containers to open windows on the host display
xhost +local:docker
```

### 2.2 Start the full stack

```bash
docker compose up --build
```

This starts the following services:

| Service | Container | Description |
|---|---|---|
| `sunrise` | `sunrise` | Main middleware (bridge, mission_controller, mock GUI) |
| `tactigon-speech-socket` | `tactigon-speech-socket` | DeepSpeech ASR socket server |
| `sunrise-comau` | `sunrise-comau` | COMAU Racer 7 ROS 2 Humble driver |
| `fiware-orion` | `fiware-orion` | NGSI-LD Context Broker |
| `mongodb` | `fiware-mongodb` | MongoDB backend for Orion-LD |
| `sunrise-timescaledb` | `sunrise-timescaledb` | TimescaleDB for TRoE and telemetry |
| `sunrise-mintaka` | `sunrise-mintaka` | NGSI-LD Temporal Retrieval API (port 8080) |
| `sunrise-grafana` | `sunrise-grafana` | Grafana dashboard (port 3000) |

**Expected output (abridged):**
```
[+] Running 8/8
 ✔ Container fiware-mongodb       Started
 ✔ Container sunrise-timescaledb  Started
 ✔ Container fiware-orion         Started
 ✔ Container sunrise-mintaka      Started
 ✔ Container sunrise-grafana      Started
 ✔ Container tactigon-speech-socket Started
 ✔ Container sunrise-comau        Started
 ✔ Container sunrise              Started
```

Grafana is available at **http://localhost:3000** (credentials: `admin` / `admin`).

### 2.3 Open a shell in the sunrise container

```bash
docker exec -it sunrise bash
source /opt/vulcanexus/jazzy/setup.bash
source /sunrise/install/setup.bash
```

---

## 3. Option B — Native ROS 2 Build

### 3.1 Install Vulcanexus Jazzy

Follow the official Vulcanexus installation guide:
[https://docs.vulcanexus.org/en/jazzy/](https://docs.vulcanexus.org/en/jazzy/)

```bash
source /opt/vulcanexus/jazzy/setup.bash
```

### 3.2 Clone the repository

```bash
git clone https://github.com/TactigonTeam/Tactigon-Sunrise.git
cd Tactigon-Sunrise
```

### 3.3 Install Python dependencies

```bash
pip3 install tactigon-gear==5.5.2 PyQt5 --break-system-packages
```

### 3.4 Build ROS 2 packages (in order)

```bash
colcon build --packages-select comau_msgs
source install/setup.bash

colcon build --packages-select sunrise_msgs
colcon build --packages-select camera_tracking
colcon build --packages-select sunrise
source install/setup.bash
```

### 3.5 Start the FIWARE monitoring stack (optional)

```bash
cd sunrise_fiware
docker compose up -d
cd ..
```

---

## 4. Software Dependencies

### Main Sunrise Container (`Dockerfile`)

Base image: `eprosima/vulcanexus:jazzy-base`

| Package | Version | Purpose |
|---|---|---|
| `tactigon-gear` | 5.5.2 | Tactigon-Skin BLE SDK (gesture + speech) |
| `PyQt5` | latest | GUI for `sunrise_tactigon_mock` |
| `python3-pyaudio` | system | Audio I/O for speech recognition |
| `bluetooth` / `bluez` / `libbluetooth-dev` | system | Bluetooth stack |
| `libboost-all-dev` | system | C++ Boost libraries |
| `python3-colcon-common-extensions` | system | ROS 2 build system |

### COMAU Driver Container (`sunrise_robot/Dockerfile`)

Base image: `eprosima/vulcanexus:humble-base`

| Package | Purpose |
|---|---|
| `ros-humble-ros2-controllers` | Controller framework |
| `ros-humble-ros2-control` | Hardware abstraction layer |
| `ros-humble-controller-manager` | Controller lifecycle management |
| `ros-humble-trajectory-msgs` | Joint trajectory messages |
| `ros-humble-rviz2` | Visualization |

### Integration Service Container (`sunrise_fiware/Dockerfile`)

Base image: `eprosima/vulcanexus:humble-base`

| Package | Purpose |
|---|---|
| `libyaml-cpp-dev` | YAML config parsing |
| `libcurlpp-dev` / `libcurl4-openssl-dev` | FIWARE HTTP client |
| eProsima Integration Service | ROS 2 → FIWARE bridge |

---

## 5. Hardware Dependencies

| Hardware | Interface | Config file |
|---|---|---|
| Tactigon-Skin wearable (right-hand) | Bluetooth LE | `config/sunrise_tactigon.json` → `"address": "C0:83:2A:34:25:38"` |
| Arduino Braccio | Bluetooth LE | `config/sunrise_braccio.json` |
| COMAU Racer 7-1.4 | Ethernet (ROS 2 Action) | `config/sunrise_comau.json` |
| USB / CSI Camera | V4L2 (`/dev/video*`) | `config/camera_tracking.json` |

**None of the above are required for the Hello World path** — see Section 6.

---

## 6. Hello World (Hardware-Free)

This minimal example starts the core middleware stack and verifies that gesture events flow from the mock GUI to the mission controller. **No hardware is required.**

### 6.1 Start the nodes

Open three separate terminals (or use `tmux`):

**Terminal 1 — Mission Controller**
```bash
source install/setup.bash
ros2 run sunrise mission_controller config/mission_controller.json
```

Expected output:
```
[mission_controller]: Node started. State: IDLE
[mission_controller]: Subscribed to /sunrise/mission_controller/intent
[mission_controller]: Subscribed to /sunrise/mission_controller/action
```

**Terminal 2 — Bridge**
```bash
source install/setup.bash
ros2 run sunrise sunrise_bridge config/sunrise_bridge.json
```

Expected output:
```
[sunrise_bridge]: Node started
[sunrise_bridge]: Subscribed to /human/body/person1/gesture
[sunrise_bridge]: Subscribed to /human/voices/person1/livespeech
```

**Terminal 3 — Mock Wearable GUI**
```bash
source install/setup.bash
ros2 run sunrise sunrise_mock
```

Expected output:
```
[sunrise_mock]: PyQt5 GUI opened
```
A PyQt5 window opens with gesture and transcription input fields.

### 6.2 Send a sample gesture event

1. In the mock GUI window, set:
   - **Type:** `HAND`
   - **Payload:** `twist`
2. Click **Send Gesture**.

**Expected output in Terminal 2 (bridge):**
```
[sunrise_bridge]: Gesture received: type=HAND payload=twist
[sunrise_bridge]: Mapping: repeat_task
[sunrise_bridge]: Publishing Intent type=REPEAT payload={"task_name": ...}
```

**Expected output in Terminal 1 (mission_controller):**
```
[mission_controller]: Intent received: type=REPEAT
[mission_controller]: State transition: IDLE → REPEAT
```

### 6.3 Verify via ROS 2 CLI

In a fourth terminal:
```bash
source install/setup.bash

# Confirm gesture topic is publishing
ros2 topic echo /human/body/person1/gesture

# Confirm bridge output
ros2 topic echo /sunrise/mission_controller/intent
ros2 topic echo /sunrise/mission_controller/action
```

Sample output for `/human/body/person1/gesture`:
```yaml
type: 0
payload: twist
---
```

Sample output for `/sunrise/mission_controller/intent`:
```yaml
type: 1
payload: '{"task_name": "solder_1"}'
---
```

### 6.4 Verify all nodes are running

```bash
ros2 node list
```

Expected output:
```
/mission_controller
/sunrise_bridge
/sunrise_mock
```

---

## 7. Using the Interactive Launcher (`launch.sh`)

The `launch.sh` script provides an interactive menu to start/stop individual nodes inside the Docker container:

```bash
./launch.sh
```

Follow the on-screen menu to start `sunrise_bridge`, `mission_controller`, `sunrise_mock`, or the full FIWARE monitoring stack.

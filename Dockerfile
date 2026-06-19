# ============================================================
#  SUNRISE – Docker Image
#  Base: ROS 2 Jazzy (Ubuntu 24.04)
# ============================================================
FROM eprosima/vulcanexus:jazzy-base

# ── System dependencies ──────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-pip \
    python3-dev \
    build-essential \
    libboost-all-dev \
    python3-pyaudio \
    bluetooth \
    bluez \
    libbluetooth-dev \
    && rm -rf /var/lib/apt/lists/*

# ── Python packages ──────────────────────────────────────────
RUN python3 -m pip install --no-cache-dir --break-system-packages tactigon-gear==5.5.2 PyQt5

# ── Create workspace ─────────────────────────────────────────
ENV ROS_WS=/sunrise
WORKDIR ${ROS_WS}

RUN mkdir -p src
RUN mkdir -p src/comau_msgs
RUN mkdir -p config
RUN mkdir -p data

# ── Copy Sunrise code ─────────────────────────────────────────
COPY src/ src/
COPY config/ config/
COPY data/ data/

# ── Copy COMAU msgs dependecy ─────────────────────────────────
COPY sunrise_robot/COMAU-ROS2-DRIVER/comau_ros2_client/comau_msgs/ src/comau_msgs/

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

SHELL ["/bin/bash", "-c"]
RUN source /opt/vulcanexus/jazzy/setup.bash && \
    colcon build --packages-select comau_msgs && \
    source ./install/setup.bash && \
    colcon build --packages-select sunrise_msgs && \
    colcon build --packages-select camera_tracking && \
    colcon build --packages-select sunrise

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
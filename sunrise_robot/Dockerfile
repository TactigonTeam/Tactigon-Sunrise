# ============================================================
#  MyCo Robot — ROS2 Humble + Comau/MyCo-ROS2
#  Base: Ubuntu 22.04 (Jammy) + ROS2 Humble Desktop Full
# ============================================================
FROM osrf/ros:humble-desktop-full

ARG DEBIAN_FRONTEND=noninteractive

# ── System deps ─────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Build tools
    build-essential \
    cmake \
    git \
    # ROS2 controllers / MoveIt
    ros-humble-joint-trajectory-controller \
    ros-humble-controller-manager \
    ros-humble-trajectory-msgs \
    ros-humble-gazebo-ros2-control \
    ros-humble-gazebo-ros-pkgs \
    ros-humble-ros2controlcli \
    ros-humble-ros2-controllers \
    ros-humble-joint-state-broadcaster \
    ros-humble-position-controllers \
    ros-humble-moveit \
    # GUI & Python deps (myco_basic_api panel)
    libgtk-3-dev \
    python3-wxgtk4.0 \
    python3-transforms3d \
    # X11 / display utilities
    x11-apps \
    libgl1-mesa-glx \
    libgl1-mesa-dri \
    mesa-utils \
    # Networking / utilities
    net-tools \
    iputils-ping \
    iproute2 \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# ── Create workspace and clone repo ─────────────────────────
ENV ROS_WS=/ros2_ws
WORKDIR ${ROS_WS}/src
RUN git clone https://github.com/Comau/MyCo-ROS2.git myco_robot

# ── Install rosdep dependencies ──────────────────────────────
WORKDIR ${ROS_WS}

# Pacchetti che rosdep non riesce a risolvere automaticamente su Humble:
#   - joint-state-publisher: nome errato nel rosdep cache (apt lo conosce)
#   - warehouse-ros-mongo: non disponibile su apt Humble, skippiamo
RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-humble-joint-state-publisher \
    ros-humble-joint-state-publisher-gui \
    && rm -rf /var/lib/apt/lists/*

# rosdep: ignora gli errori irrisolvibili (warehouse-ros-mongo) con || true
RUN . /opt/ros/humble/setup.sh && \
    rosdep update && \
    rosdep install --from-paths src --ignore-src -r -y \
      --skip-keys "rviz warehouse_ros_mongo" || true

# ── Build ────────────────────────────────────────────────────
# soem_ros2 (EtherCAT) ha un warning strncpy trattato come errore
# dal GCC di Ubuntu 22.04 → disabilitiamo solo quell'errore per SOEM
RUN . /opt/ros/humble/setup.sh && \
    colcon build \
      --symlink-install \
      --cmake-args \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_C_FLAGS="-Wno-error=stringop-truncation" \
        -DCMAKE_CXX_FLAGS="-Wno-error=stringop-truncation" \
    && rm -rf build/*/test_results \
    && chmod +x /ros2_ws/install/myco_basic_api/lib/myco_basic_api/*.py

# ── Entrypoint ───────────────────────────────────────────────
COPY ros_entrypoint.sh /ros_entrypoint.sh
RUN chmod +x /ros_entrypoint.sh

# ── Shell defaults ───────────────────────────────────────────
RUN echo "source /opt/ros/humble/setup.bash" >> /root/.bashrc && \
    echo "source ${ROS_WS}/install/setup.bash" >> /root/.bashrc && \
    echo "export ROS_DOMAIN_ID=\${ROS_DOMAIN_ID:-42}" >> /root/.bashrc

WORKDIR ${ROS_WS}
ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["bash"]
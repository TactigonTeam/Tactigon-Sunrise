# ============================================================
#  COMAU ROS2 Driver – Docker Image
#  Base: ROS 2 Humble (Ubuntu 22.04)
# ============================================================
FROM eprosima/vulcanexus:humble-base

# ── System dependencies ──────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-pip \
    libboost-all-dev \
    ros-humble-ros2-controllers \
    ros-humble-ros2-control \
    ros-humble-controller-manager \
    ros-humble-hardware-interface \
    ros-humble-joint-limits \
    ros-humble-trajectory-msgs \
    ros-humble-control-msgs \
    ros-humble-action-msgs \
    ros-humble-xacro \
    ros-humble-joint-state-publisher \
    ros-humble-joint-state-publisher-gui \
    ros-humble-robot-state-publisher \
    ros-humble-rviz2 \
    # ros-humble-rmw-fastrtps-cpp \
    && rm -rf /var/lib/apt/lists/*

# ── Fix include path per joint_limits ────────────────────────
RUN ln -s \
    /opt/ros/humble/include/joint_limits/joint_limits \
    /usr/include/joint_limits

# ── Create workspace ─────────────────────────────────────────
ENV ROS_WS=/comau_driver
WORKDIR ${ROS_WS}

RUN mkdir -p src

# ── Copy COMAU driver ────────
COPY COMAU-ROS2-DRIVER/comau_ros2_client/ src/

# ── rosdep install ────────────────────────────────────────────
RUN rosdep update --include-eol-distros && \
    rosdep install --from-paths src --ignore-src -r -y \
      --skip-keys "Boost rviz2 joint_state_publisher_gui" || true

# ── Build package --------──────────────────────────────────────
SHELL ["/bin/bash", "-c"]
RUN source /opt/vulcanexus/humble/setup.bash && \
    colcon build --packages-skip comau_bringup && \
    source ./install/setup.bash && \
    colcon build --packages-select comau_bringup

# ── Entrypoint driver (robot reale) ──────────────────────────
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
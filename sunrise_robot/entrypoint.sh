#!/bin/bash
set -e

# Source ROS2 environment
source /opt/ros/humble/setup.bash
source /ros2_humble/install/setup.bash

# Launch with ROBOT_MODEL
echo "[entrypoint] Launching with robot_type=${ROBOT_MODEL}"
exec ros2 launch comau_bringup start_comau_client.launch.py robot_type:=${ROBOT_MODEL}
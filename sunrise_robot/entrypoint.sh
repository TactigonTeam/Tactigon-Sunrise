#!/bin/bash
set -e

# Source ROS2 environment
source /opt/vulcanexus/humble/setup.bash
source /comau_driver/install/setup.bash 

# Launch with ROBOT_MODEL
echo "[entrypoint] Launching with robot_type=${ROBOT_MODEL}"
exec ros2 launch comau_bringup start_comau_client.launch.py robot_type:=${ROBOT_MODEL}
#!/bin/bash
set -e

# Source ROS2 Humble
source /opt/ros/humble/setup.bash

# Source workspace (if built)
if [ -f "/ros2_ws/install/setup.bash" ]; then
    source /ros2_ws/install/setup.bash
fi

# Set ROS_DOMAIN_ID (default 42, override via env)
export ROS_DOMAIN_ID=${ROS_DOMAIN_ID:-42}

# For GUI apps: use host X11 if DISPLAY is set
if [ -n "$DISPLAY" ]; then
    echo "[myco] DISPLAY=$DISPLAY — GUI apps enabled"
fi

exec "$@"
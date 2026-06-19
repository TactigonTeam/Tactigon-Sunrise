#!/bin/bash
set -e

# Source ROS2 environment
source /opt/vulcanexus/jazzy/setup.bash
source /sunrise/install/setup.bash 

# Launch with ROBOT_MODEL
echo "[entrypoint] Launching Sunrise Bridge"
# exec ros2 run sunrise sunrise_mock
# # exec ros2 run sunrise sunrise_tactigon ./config/sunrise_tactigon.json
# exec ros2 run sunrise sunrise_bridge ./config/sunrise_bridge.json
# exec ros2 run sunrise mission_controller ./config/mission_controller.json
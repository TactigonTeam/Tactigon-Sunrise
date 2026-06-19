#!/bin/bash

rm -rf build install log
colcon build --symlink-install --packages-select comau_msgs
source ./install/setup.bash
colcon build --symlink-install --packages-select sunrise_msgs
source ./install/setup.bash
colcon build --symlink-install --packages-select camera_tracking
source ./install/setup.bash
colcon build --symlink-install --packages-select sunrise
source ./install/setup.bash

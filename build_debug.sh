rm -rf build install log
colcon build --symlink-install --packages-select sunrise_msgs
colcon build --symlink-install --packages-select camera_tracking
colcon build --symlink-install --packages-select sunrise

rm -rf build install log
colcon build --symlink-install --packages-select sunrise_msgs
colcon build --symlink-install --packages-select braccio_ros_msgs
colcon build --symlink-install --packages-select braccio_ros
colcon build --symlink-install --packages-select sunrise
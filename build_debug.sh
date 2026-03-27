rm -rf build install log
colcon build --symlink-install --packages-select sunrise_msgs
colcon build --symlink-install --packages-select comau_msgs
colcon build --symlink-install --packages-select braccio_ros_msgs
colcon build --symlink-install --packages-select braccio_ros
colcon build --symlink-install --packages-select sunrise_comau
colcon build --symlink-install --packages-select camera_tracking
colcon build --symlink-install --packages-select sunrise

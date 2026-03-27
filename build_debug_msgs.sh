rm -rf build install log
colcon build --symlink-install --packages-select sunrise_msgs
colcon build --symlink-install --packages-select sunrise_comau_msgs

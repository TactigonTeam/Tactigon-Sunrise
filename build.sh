rm -rf build install log
colcon build --packages-select sunrise_msgs
colcon build --packages-select camera_tracking
colcon build --packages-select sunrise
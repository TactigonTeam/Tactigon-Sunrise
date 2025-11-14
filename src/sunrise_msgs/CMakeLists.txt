cmake_minimum_required(VERSION 3.8)
project(sunrise_msgs)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/Action.msg"
  "msg/Intent.msg"
  DEPENDENCIES builtin_interfaces
)

ament_package()

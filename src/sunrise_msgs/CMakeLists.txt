cmake_minimum_required(VERSION 3.8)
project(sunrise_msgs)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)
find_package(comau_msgs REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/Gesture.msg"
  "msg/Transcription.msg"
  "msg/Action.msg"
  "msg/Intent.msg"
  "msg/Point2D.msg"
  "msg/Marker.msg"
  "msg/MarkerList.msg"
  "msg/BraccioCommand.msg"
  "msg/BraccioJointCommand.msg"
  "msg/BraccioResponse.msg"
  DEPENDENCIES builtin_interfaces
  DEPENDENCIES std_msgs
  DEPENDENCIES comau_msgs
)

ament_package()

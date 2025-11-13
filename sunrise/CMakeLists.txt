cmake_minimum_required(VERSION 3.8)
project(sunrise)

find_package(ament_cmake REQUIRED)
find_package(rclpy REQUIRED)
find_package(sunrise_msgs REQUIRED)

install(
  PROGRAMS
    sunrise/main.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
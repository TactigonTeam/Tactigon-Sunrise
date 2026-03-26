# Copyright 2024 Comau Robotics S.p.A.

from launch_ros.substitutions import FindPackageShare

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution, TextSubstitution
from launch import LaunchService
import sys
import launch.actions
import launch.events

def generate_launch_description():
    """Main."""
    
    robot_type = ""
    
    for arg in sys.argv:
        if arg.startswith("robot_type:="):
            robot_type = str(arg.split(":=")[1])
    
    match robot_type:
        case "racer7-14":
            return LaunchDescription([
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource([
                    PathJoinSubstitution([
                        FindPackageShare('racer7-14_description'),
                        'launch/',
                        'view_racer7-14.launch.py'
                    ])
                ]),
            )
        ])
        case _:
            print("Client closed. Please choose a robot_type:=\n racer7-14")
            sys.exit()
    
    return

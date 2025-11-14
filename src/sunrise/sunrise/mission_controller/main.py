import sys
import rclpy
from rclpy.logging import get_logger

from sunrise.mission_controller.node import MissionController

def main(args=None):
    config_path = sys.argv[1] if len(sys.argv) > 1 else None

    if not config_path:
        get_logger("mission_controller").error("Cannot start mission controller node. Config file path is missing")
        return
    
    spin_node(config_path, args)

def spin_node(config_path: str, args=None):
    rclpy.init(args=args)

    node = MissionController(config_path)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()

    rclpy.try_shutdown()
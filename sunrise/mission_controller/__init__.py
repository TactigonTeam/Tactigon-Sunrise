import rclpy

from typing import Callable

from sunrise.mission_controller.node import MissionControllerNode
from sunrise.mission_controller.models import MissionControllerConfig, Message, NodeAction, NodeActions

class MissionController:
    def __init__(self, config: MissionControllerConfig, fn: Callable[[MissionControllerNode, Message], None]):
        self._config = config
        self._callback = fn

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *attr):
        pass

    def start(self):
        rclpy.init()
        try:
            self.node = MissionControllerNode()

            for p in self._config.publishers:
                self.node.add_publisher(p.topic, p.message_type, p.qos_profile)

            for s in self._config.subscriptions:
                self.node.add_subscription(s.topic, self._callback, s.message_type, s.qos_profile)
            
            rclpy.spin(self.node)
        except Exception as e:
            print(e)
        finally:
            rclpy.try_shutdown()

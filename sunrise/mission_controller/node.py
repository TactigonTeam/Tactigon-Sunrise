
from rclpy.node import Node, QoSProfile
from functools import wraps

from typing import Callable, Any

from sunrise.mission_controller.models import Message

class MissionControllerNode(Node):
    TICK: float = 0.02

    def __init__(self):
        Node.__init__(self, "sunrise_mission_controller")

    def add_publisher(self, topic: str, message_type: Any, qos_profile: QoSProfile | int):
        publisher = self.create_publisher(message_type, topic, qos_profile)

    def add_subscription(self, topic: str, fn: Callable[["MissionControllerNode", Message], None], message_type: Any, qos_profile: QoSProfile | int):
        self.create_subscription(
            message_type, 
            topic, 
            self._callback(topic, fn), 
            qos_profile
        )

    def publish(self, topic: str, message_type: Any, msg: Any):
        publisher = next((p for p in self.publishers if p.topic == topic), None)

        if publisher:
            message = message_type()
            message.data = msg
            publisher.publish(message)

    def unsubscribe(self, topic: str):
        subscription = next((s for s in self.subscriptions if s.topic == topic), None)

        if subscription:
            self.destroy_subscription(subscription)

    def _callback(self, topic: str, fn: Callable[["MissionControllerNode", Message], None]):
        @wraps(fn)
        def wrapper(msg, *args):
            return fn(self, Message(topic, msg))
        return wrapper

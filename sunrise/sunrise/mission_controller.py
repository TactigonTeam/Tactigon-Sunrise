import json
from rclpy.logging import LoggingSeverity
from rclpy.node import Node, QoSProfile
from functools import wraps

from typing import Callable, Any

from sunrise.sunrise.models.sunrise import SunriseConfig, MissionControllerConfig
from sunrise.sunrise.models.mission_controller import Message
from sunrise.sunrise.teacher import Teacher
from sunrise.sunrise.student import Student

class MissionController(Node):

    _config_path: str
    _config: MissionControllerConfig
    teacher: Teacher
    student: Student

    def __init__(self, config_path: str):
        Node.__init__(self, MissionController.__name__)
        self.get_logger().set_level(LoggingSeverity.DEBUG)
        self.get_logger().info(f"Creating node {MissionController.__name__}")

        self._config_path = config_path
        _config = self.load_config(config_path)
        
        self._config = _config.mission_controller

        self.teacher = Teacher(_config.teacher_config_path)
        self.studend = Student(_config.student_config_path)

        for p in self._config.publishers:
            self.add_publisher(p.topic, p.message_type, p.qos_profile)

        for s in self._config.subscriptions:
            self.add_subscription(s.topic, s.message_type, s.qos_profile)

        self.get_logger().info(f"Created!")

    def load_config(self, config_path: str) -> SunriseConfig:
        with open(config_path) as cf:
            return SunriseConfig.FromJSON(json.load(cf))

    def add_publisher(self, topic: str, message_type: Any, qos_profile: QoSProfile | int):
        self.get_logger().info(f"Adding publisher {topic}, {message_type}")
        self.create_publisher(message_type, topic, qos_profile)

    def add_subscription(self, topic: str, message_type: Any, qos_profile: QoSProfile | int):
        self.get_logger().info(f"Adding subscriber {topic}, {message_type}")
        self.create_subscription(
            message_type, 
            topic, 
            self._callback(topic, self.state_machine), 
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

    def _callback(self, topic: str, fn: Callable[[Message], None]):
        @wraps(fn)
        def wrapper(msg, *args):
            return fn(Message(topic, msg))
        return wrapper
    
    def state_machine(self, message: Message):
        print(message)
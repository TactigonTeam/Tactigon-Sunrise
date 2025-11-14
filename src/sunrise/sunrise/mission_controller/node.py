#********************************************************************************
# Copyright (c) 2025 Next Industries s.r.l.
#
# This program and the accompanying materials are made available under the
# terms of the Apache 2.0 which is available at http://www.apache.org/licenses/LICENSE-2.0
#
# SPDX-License-Identifier: Apache-2.0
#
# Contributors:
# Massimiliano Bellino
# Stefano Barbareschi
#********************************************************************************/

import json
from rclpy.logging import LoggingSeverity
from rclpy.node import Node, QoSProfile
from rclpy.time import Time

from functools import wraps
from enum import Enum
from datetime import datetime

from sunrise_msgs.msg import Action, Intent

from typing import Callable, Any

from sunrise.mission_controller.models.mission_controller import MissionControllerConfig, Message
from sunrise.mission_controller.teo import TEO
from sunrise.mission_controller.teo.models import Skill, SkillScope
from sunrise.mission_controller.leo import LEO

class MachineState(Enum):
    IDLE = 0
    TEACH = 1
    REPEAT = 2

class ActionType(Enum):
    GESTURE = 0
    VOICE_COMMAND = 1


class MissionController(Node):

    _config_path: str
    _config: MissionControllerConfig

    teacher: TEO
    student: LEO
    state: tuple[Time, MachineState, dict]
    
    _actions: list[tuple[Time, Action]]

    def __init__(self, config_path: str):
        Node.__init__(self, MissionController.__name__)
        self.get_logger().set_level(LoggingSeverity.DEBUG)
        
        self.info(f"Creating node {MissionController.__name__}")

        self._config_path = config_path
        self._config = self.load_config(config_path)
        
        self.teacher = TEO(self._config.teacher_config_path)
        self.studend = LEO(self._config.student_config_path)

        for p in self._config.publishers:
            self.add_publisher(p.topic, p.message_type, p.qos_profile)

        for s in self._config.subscriptions:
            self.add_subscription(s.topic, s.message_type, s.qos_profile)

        self.action_timer = self.create_timer(0.1, self._clear_expired_actions)
        self.state_timer = self.create_timer(3, self._clear_state)
        self.do_state_timer = self.create_timer(0.05, self.do_state)

        self.state = (self.now(), MachineState.IDLE, {})
        self._actions = []

        self.info(f"Created!")

    def load_config(self, config_path: str) -> MissionControllerConfig:
        with open(config_path) as cf:
            return MissionControllerConfig.FromJSON(json.load(cf))

    def add_publisher(self, topic: str, message_type: Any, qos_profile: QoSProfile | int):
        self.info(f"Adding publisher {topic}, {message_type}")
        self.create_publisher(message_type, topic, qos_profile)

    def add_subscription(self, topic: str, message_type: Any, qos_profile: QoSProfile | int):
        self.info(f"Adding subscriber {topic}, {message_type}")
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

    # def unsubscribe(self, topic: str):
    #     subscription = next((s for s in self.subscriptions if s.topic == topic), None)

    #     if subscription:
    #         self.destroy_subscription(subscription)

    def debug(self, msg: str):
        self.get_logger().debug(msg)

    def info(self, msg: str):
        self.get_logger().info(msg)

    def warn(self, msg: str):
        self.get_logger().warn(msg)

    def error(self, msg: str):
        self.get_logger().error(msg)

    def now(self) -> Time:
        return self.get_clock().now()

    def _callback(self, topic: str, fn: Callable[[Message], None]):
        @wraps(fn)
        def wrapper(msg, *args):
            return fn(Message(topic, msg, self.now()))
        return wrapper
    
    def _clear_expired_actions(self):
        if not self._actions:
            return
        
        now = self.now()
        self._actions = [a for a in self._actions if (now-a[0]).nanoseconds < 3*10e7]

        self.debug(f"Valid actions count: {len(self._actions)}")

    def _clear_state(self):
        if self.state[1] == MachineState.IDLE:
            return
        
        now = self.now()

        if (now - self.state[0]).nanoseconds > 5*10e7:
            self._reset_state()

    def _reset_state(self):
        self.state = (self.now(), MachineState.IDLE, {})

    def _map_intent_to_state(self, timestamp: Time, intent: Intent):
        if self.state[1] is not MachineState.IDLE:
            self.warn(f"Trying to state machine state while the state is {self.state}. Discard.")
            return
        
        state = MachineState.IDLE
        payload = json.loads(intent.payload)
        
        if intent.type == Intent.TEACH:
            state = MachineState.TEACH
        elif intent.type == Intent.REPEAT:
            state = MachineState.REPEAT

        self.state = (timestamp, state, payload)
        self.debug(f"Updated state machine to {self.state}")

    def _map_action(self, timestamp: Time, action: Action):
        self._actions.append((timestamp, action))

    def state_machine(self, message: Message):
        self.debug(f"Received {message.topic} > {message.msg}")

        if isinstance(message.msg, Intent):
            self._map_intent_to_state(message.timestamp, message.msg)
            
        if isinstance(message.msg, Action):
            self._map_action(message.timestamp, message.msg)

    def do_state(self):
        timestamp, state, payload = self.state
        
        if state == MachineState.IDLE:
            return
        
        self.debug(f"Managing action for state {state} | {payload}")
        
        if state == MachineState.TEACH:
            if self._actions:
                time, action = self._actions.pop(0)

                self.debug(f"Learning skill {payload} => {action}")
                
                s = Skill(
                    scope=SkillScope.BRACCIO_ROBOT,
                    name=payload.get("skill", ""),
                    payload=json.loads(action.payload)
                )
                
                self.teacher.add_skill(s)
                self.teacher.save_config()

                self._reset_state()




            
        
            
                


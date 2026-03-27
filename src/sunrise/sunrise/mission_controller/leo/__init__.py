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
#********************************************************************************

import json
import time

from enum import Enum
from functools import wraps
from typing import Callable

from rclpy.publisher import Publisher
from rclpy.logging import RcutilsLogger

from threading import Event

from sunrise.mission_controller.models.mission_controller import Message
from sunrise.mission_controller.leo.models import LEOConfig
from sunrise.mission_controller.models.task import Task
from sunrise.mission_controller.models.skill import Skill

from sunrise.mission_controller.msg import RosMessageTypes

class TaskErrorEnum(Enum):
    NO_ERROR = 0
    TASK_NOT_FOUND = 1
    ROBOT_DEFINITION_NOT_FOUND = 2
    COMMAND_NOT_FOUND = 3
    EXECUTION_ERROR = 4

class StepErrorEnum(Enum):
    UNDEFINED = -1
    NO_ERROR = 0
    NOT_EXECUTED = 1

class LEO:
    _config: LEOConfig
    _pubblisher: dict[str, Publisher]
    # _topic_response: tuple[str, StepErrorEnum] | None
    # _topic_response_event: Event

    def __init__(self, config_path: str, logger: RcutilsLogger):
        self._config = self.load_config(config_path)
        self._logger = logger
        self._pubblisher = {}
        # self._topic_response_event = Event()

    def load_config(self, config_path: str) -> LEOConfig:
        with open(config_path) as cf:
            return LEOConfig.FromJSON(json.load(cf))
    
    def get_publishers_from_config(self) -> set[tuple[str, RosMessageTypes]]:
        return set(((command.command_topic, command.command_topic_type) for robot in self._config.robots for command in robot.commands))
    
    # def get_subscribers_from_config(self) -> set[tuple[str, RosMessageTypes]]:
    #     return set(((command.response_topic, command.response_topic_type) for robot in self._config.robots for command in robot.commands))

    # def subscription_callback(self, msg: Message):
    #     self._logger.debug(f"LEO got message {msg}")

    #     if not self._topic_response:
    #         return

    #     if self._topic_response[0] == msg.topic:
    #         step_error = StepErrorEnum.NO_ERROR if msg.msg.get("success", False) else StepErrorEnum.NOT_EXECUTED
    #         self._topic_response = (msg.topic, step_error)
    #         self._topic_response_event.set()
        
    def add_publisher(self, topic: str, publisher: Publisher):
        if self._pubblisher.get(topic, False):
            return

        self._pubblisher[topic] = publisher

    def get_publisher(self, topic: str) -> Publisher | None:
        return self._pubblisher.get(topic, None)

    def repeat_task(self, task: Task | None, payload: dict) -> TaskErrorEnum:
        if not task:
            return TaskErrorEnum.TASK_NOT_FOUND
        
        for s in task.skills:
            error = self.do_skill(s)
            if error is not TaskErrorEnum.NO_ERROR:
                return error

        return TaskErrorEnum.NO_ERROR

    def do_skill(self, skill: Skill) -> TaskErrorEnum:
        robot = self._config.get_robot(skill.scope)

        if not robot:
            return TaskErrorEnum.ROBOT_DEFINITION_NOT_FOUND
        
        command = robot.get_command(skill.name)

        if not command:
            return TaskErrorEnum.COMMAND_NOT_FOUND
        
        pub = self.get_publisher(command.command_topic)

        if not pub:
            return TaskErrorEnum.COMMAND_NOT_FOUND
        
        for step in command.steps:
            msg_data = {}
            self._logger.debug(f"Step items {step.payload_fields.items()}")
            for key, value in step.payload_fields.items():
                self._logger.debug(f"LOADING: {key}, {value}")
                self._logger.debug(f"SKILL: {skill}")

                if value.is_list:
                    if value.override and key in skill.payload:
                        self._logger.debug(f"OVERRIDE LIST: {skill.payload[key]}")
                        typed_value = [value.payload_type(**v) for v in skill.payload[key]]
                    else:
                        typed_value = [value.payload_type(value.default)]
                else:
                    if value.override and key in skill.payload:
                        self._logger.debug(f"OVERRIDE: {skill.payload[key]}")
                        typed_value = value.payload_type(skill.payload[key])
                    else:
                        typed_value = value.payload_type(value.default)

                self._logger.debug(f"FINAL: {typed_value}")
                msg_data[key] = typed_value
            
            self._logger.debug(f"Student -> Sending msg to {robot.name} with payload {msg_data}")
            msg: RosMessageTypes = command.command_topic_type(**msg_data) # type: ignore
            self._logger.debug(f"Student -> Sending msg {msg}")
            pub.publish(msg)
            # self._topic_response_event.clear()
            # self._topic_response = (command.command_topic, StepErrorEnum.UNDEFINED)

            # received = self._topic_response_event.wait(10)
            # if not received or self._topic_response[1] != StepErrorEnum.NO_ERROR:
            #     self._topic_response = None
            #     return TaskErrorEnum.EXECUTION_ERROR
            
        # self._topic_response = None
        
        return TaskErrorEnum.NO_ERROR

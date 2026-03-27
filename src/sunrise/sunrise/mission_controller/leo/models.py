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

from dataclasses import dataclass

from typing import Any

from sunrise.mission_controller.models.robots import RobotDefinition
from sunrise.mission_controller.models.skill import Skill
from sunrise.mission_controller.msg import RosMessageTypes, get_message_type_by_name, get_message_name

@dataclass
class RosMessage:
    topic: str
    msg: RosMessageTypes

@dataclass
class CommandStepField:
    default: Any
    payload_type: RosMessageTypes
    is_list: bool = False
    override: bool = False

    @classmethod
    def FromJSON(cls, json: dict):
        return cls(
            default=json.get("default", None),
            payload_type=get_message_type_by_name(json.get("payload_type", "String")),
            is_list=json.get("is_list", False),
            override=json.get("override", False),
        )
    
    def toJSON(self) -> dict:
        return dict(
            default=self.default,
            payload_type=self.payload_type.__name__,
            is_list=self.is_list,
            override=self.override,
        )

@dataclass
class CommandStep:
    payload_fields: dict[str, CommandStepField]

    @classmethod
    def FromJSON(cls, json: dict):
        return cls(
            payload_fields={
                key: CommandStepField.FromJSON(value)
                for key, value in json.get("payload_fields", {}).items()
            }
        )
    
    def toJSON(self) -> dict:
        return dict(
            payload_fields={
                key: field.toJSON()
                for key, field in self.payload_fields.items()
            }
        )


@dataclass
class Command:
    command_name: str
    command_topic: str
    command_topic_type: RosMessageTypes
    response_topic: str
    response_topic_type: RosMessageTypes
    steps: list[CommandStep]

    @classmethod
    def FromJSON(cls, json: dict):
        return cls(
            command_name=json.get("command_name", ""),
            command_topic=json.get("command_topic", ""),
            command_topic_type=get_message_type_by_name(json.get("command_topic_type", "String")),
            response_topic=json.get("response_topic", ""),
            response_topic_type=get_message_type_by_name(json.get("response_topic_type", "String")),
            steps=[CommandStep.FromJSON(s) for s in json.get("steps", [])]
        )
    
    def toJSON(self) -> dict:
        return dict(
            command_name=self.command_name,
            command_topic=self.command_topic,
            command_topic_type=self.command_topic_type.__name__,
            response_topic=self.response_topic,
            response_topic_type=self.response_topic_type.__name__,
            steps=[s.toJSON() for s in self.steps]
        )

@dataclass
class Robot:
    name: RobotDefinition
    robot_type: str
    commands: list[Command]

    @classmethod
    def FromJSON(cls, json: dict):
        return cls(
            name=RobotDefinition(json.get("name", "")),
            robot_type=json.get("namrobot_typee", ""),
            commands=[Command.FromJSON(c) for c in json.get("commands", [])]
        )
    
    def toJSON(self) -> dict:
        return dict(
            name=self.name.value,
            robot_type=self.robot_type,
            commands=[c.toJSON() for c in self.commands]
        )

    def get_command(self, command_name: str) -> Command | None:
        return next((command for command in self.commands if command.command_name == command_name), None)

@dataclass
class LEOConfig:
    robots: list[Robot]

    @classmethod
    def FromJSON(cls, json: dict):
        return cls(
            robots=[Robot.FromJSON(r) for r in json.get("robots", [])]
        )
    
    def toJSON(self) -> dict:
        return dict(
            robots=[r.toJSON() for r in self.robots]
        )
    
    def get_robot(self, robot_name: RobotDefinition) -> Robot | None:
        return next((robot for robot in self.robots if robot.name == robot_name), None)
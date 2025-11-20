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

from rclpy.node import QoSProfile
from rclpy.time import Time

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from sunrise.mission_controller.msg import RosMessageTypes, get_message_type_by_name

@dataclass
class Message:
    topic: str
    msg: Any
    timestamp: Time

class NodeActions(Enum):
    ADD_PUBLISHER = "add_publisher"
    ADD_SUBSCRIPTION = "add_subscriber"
    PUBLISH = "publish"
    UNSUBSCRIBE = "unsubscribe"

@dataclass
class NodeAction:
    action: NodeActions
    payload: dict

    @classmethod
    def AddPubblisher(cls, payload: dict):
        return cls(
            NodeActions.ADD_PUBLISHER,
            payload
        )
    
    @classmethod
    def AddSubscription(cls, payload: dict):
        return cls(
            NodeActions.ADD_SUBSCRIPTION,
            payload
        )
    
    @classmethod
    def Publish(cls, payload: dict):
        return cls(
            NodeActions.PUBLISH,
            payload
        )
    
    @classmethod
    def Unsubscribe(cls, payload: dict):
        return cls(
            NodeActions.UNSUBSCRIBE,
            payload
        )
    
@dataclass
class Topic:
    topic: str
    message_type: RosMessageTypes
    qos_profile: QoSProfile | int = 10
    
    @classmethod
    def FromJSON(cls, json: dict):
        return cls(
            topic=json.get("topic", "missing"),
            message_type=get_message_type_by_name(json.get("message_type", "")),
            qos_profile=json.get("qos_profile", 10)
        )
    
    def toJSON(self) -> dict:
        return dict(
            topic=self.topic,
            message_type=self.message_type.__name__,
            qos_profile=self.qos_profile
        )

@dataclass
class MissionControllerConfig:
    teacher_config_path: str
    student_config_path: str
    logging: Topic
    publishers: list[Topic] = field(default_factory=list)
    subscriptions: list[Topic] = field(default_factory=list)

    @classmethod
    def FromJSON(cls, json: dict):
        return cls(
            teacher_config_path=json.get("teacher_config_path", ""),
            student_config_path=json.get("student_config_path", ""),
            logging=Topic.FromJSON(json.get("logging", {})),
            publishers=[Topic.FromJSON(json) for json in json.get("publishers", [])],
            subscriptions=[Topic.FromJSON(json) for json in json.get("subscriptions", [])],
        )
    
    def toJSON(self) -> dict:
        return dict(
            teacher_config_path=self.teacher_config_path,
            student_config_path=self.student_config_path,
            logging=self.logging.toJSON(),
            publishers=[p.toJSON() for p in self.publishers],
            subscriptions=[s.toJSON() for s in self.subscriptions],
        )
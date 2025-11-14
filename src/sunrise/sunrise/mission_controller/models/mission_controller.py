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

from rclpy.node import QoSProfile
from rclpy.time import Time

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from sunrise.mission_controller import msg

print(msg)

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
class Publisher:
    topic: str
    message_type: Any
    qos_profile: QoSProfile | int = 10

    @classmethod
    def FromJSON(cls, json: dict):
        return cls(
            json["topic"],
            getattr(msg, json["message_type"]),
            json["qos_profile"] if "qos_profile" in json and json["qos_profile"] else 10,
        )
    
    def toJSON(self) -> dict:
        return {
            "topic": self.topic,
            "message_type": self.message_type.__name__,
            "qos_profile": self.qos_profile
        }

@dataclass
class Subscription:
    topic: str
    # function: Callable[[MissionControllerNode, Message], None]
    message_type: Any
    qos_profile: QoSProfile | int = 10
    
    @classmethod
    def FromJSON(cls, json: dict):
        return cls(
            json["topic"],
            # json["function"],
            getattr(msg, json["message_type"]),
            json["qos_profile"] if "qos_profile" in json and json["qos_profile"] else 10,
        )
    
    def toJSON(self) -> dict:
        return {
            "topic": self.topic,
            # "function": self.function.__name__,
            "message_type": self.message_type.__name__,
            "qos_profile": self.qos_profile
        }

@dataclass
class MissionControllerConfig:
    teacher_config_path: str
    student_config_path: str
    publishers: list[Publisher] = field(default_factory=list)
    subscriptions: list[Subscription] = field(default_factory=list)

    @classmethod
    def FromJSON(cls, json: dict):
        return cls(
            teacher_config_path=json.get("teacher_config_path", ""),
            student_config_path=json.get("student_config_path", ""),
            publishers=[Publisher.FromJSON(json) for json in json.get("publishers", [])],
            subscriptions=[Subscription.FromJSON(json) for json in json.get("subscriptions", [])],
        )
    
    def toJSON(self) -> dict:
        return dict(
            teacher_config_path=self.teacher_config_path,
            student_config_path=self.student_config_path,
            publishers=[p.toJSON() for p in self.publishers],
            subscriptions=[s.toJSON() for s in self.subscriptions],
        )
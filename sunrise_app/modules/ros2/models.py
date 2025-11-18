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
from std_msgs.msg import String, Int16, Int32, UInt16, UInt32, Bool, Byte, Float32, Float64, Int8, UInt8, Int64, UInt64, ColorRGBA
from sunrise_msgs.msg import Action, Intent
from braccio_ros_msgs.msg import BraccioCommand, BraccioResponse

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

StrMessageTypes = String | Int64 | Bool | Float64
SunriseMessageTypes = Action | Intent
BraccioMessageTypes = BraccioCommand | BraccioResponse
RosMessageTypes = StrMessageTypes | SunriseMessageTypes | BraccioMessageTypes

def get_message_type_by_name(name: str) -> RosMessageTypes:
    type_index = [t.__name__ for t in RosMessageTypes.__args__].index(name)    
    return RosMessageTypes.__args__[type_index]

def get_message_name() -> list[str]:
    return [t.__name__ for t in RosMessageTypes.__args__]

def get_message_data(msg: RosMessageTypes) -> Any:
    data = {}
    for field in msg.get_fields_and_field_types():
        print(field)
        data[field] = getattr(msg, field)
    return data

@dataclass
class RosMessage:
    topic: str
    msg: RosMessageTypes

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
class Ros2Publisher:
    topic: str
    message_type: Any
    qos_profile: QoSProfile | int = 10

    @classmethod
    def FromJSON(cls, json: dict):
        return cls(
            json["topic"],
            get_message_type_by_name(json["message_type"]),
            json["qos_profile"] if "qos_profile" in json and json["qos_profile"] else 10,
        )
    
    def toJSON(self) -> dict:
        return {
            "topic": self.topic,
            "message_type": self.message_type.__name__,
            "qos_profile": self.qos_profile
        }

@dataclass
class Ros2Subscription:
    topic: str
    function: str
    payload_reference: str
    message_type: Any
    qos_profile: QoSProfile | int = 10
    
    @classmethod
    def FromJSON(cls, json: dict):
        return cls(
            json["topic"],
            json["function"],
            json["payload_reference"],
            get_message_type_by_name(json["message_type"]),
            json["qos_profile"] if "qos_profile" in json and json["qos_profile"] else 10,
        )
    
    def toJSON(self) -> dict:
        return {
            "topic": self.topic,
            "function": self.function,
            "payload_reference": self.payload_reference,
            "message_type": self.message_type.__name__,
            "qos_profile": self.qos_profile
        }
    
@dataclass
class Ros2ShapeConfig:
    node_name: str
    publishers: list[Ros2Publisher] = field(default_factory=list)
    subscriptions: list[Ros2Subscription] = field(default_factory=list)

    @classmethod
    def FromJSON(cls, json: dict):
        return cls(
            json.get("node_name", "sunrise_node"),
            [Ros2Publisher.FromJSON(json) for json in json.get("publishers", [])],
            [Ros2Subscription.FromJSON(json) for json in json.get("subscriptions", [])]
        )
    
    def toJSON(self) -> dict:
        return {
            "node_name": self.node_name,
            "publishers": [p.toJSON() for p in self.publishers],
            "subscriptions": [s.toJSON() for s in self.subscriptions],
        }
    
@dataclass
class Ros2Command:
    package_name: str
    node_name: str
    parameter_file: str

    @staticmethod
    def get_package_and_node_from_identifier(identifier: str) -> tuple[str, str]:
        package_name, node_name = identifier.split("]-[")
        package_name = package_name[1:]
        node_name = node_name[:-1]

        print(package_name, node_name)

        return package_name, node_name

    @classmethod
    def FromJSON(cls, json: dict):
        return cls(
            json["package_name"],
            json["node_name"],
            json["parameter_file"],
        )
    
    def toJSON(self) -> dict:
        return dict(
            package_name=self.package_name,
            node_name=self.node_name,
            parameter_file=self.parameter_file,
        )
    
    @property
    def identifier(self) -> str:
        return f"[{self.package_name}]-[{self.node_name}]"
    
    @property
    def name(self) -> str:
        return f"{self.package_name}.{self.node_name}"
    
    def get_command(self) -> str:
        return f"ros2 run {self.package_name} {self.node_name} --ros-args --params-file {self.parameter_file}"

@dataclass
class Ros2Config:
    ros2_commands: list[Ros2Command] = field(default_factory=list)

    @classmethod
    def Default(cls):
        return cls(
            []
        )

    @classmethod
    def FromJSON(cls, json: dict):
        return cls(
            [Ros2Command.FromJSON(c) for c in json.get("ros2_commands", [])]
        )
    
    def toJSON(self) -> dict:
        return dict(
            ros2_commands=[c.toJSON() for c in self.ros2_commands]
        )
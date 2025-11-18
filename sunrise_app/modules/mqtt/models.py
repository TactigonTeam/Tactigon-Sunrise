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

from paho.mqtt.enums import CallbackAPIVersion, MQTTProtocolVersion
from dataclasses import dataclass, field

from typing import Any, List

@dataclass
class MQTTMessage:
    topic: str
    payload: Any

@dataclass
class MQTTSubscription:
    topic: str
    function: str
    payload_reference: str
    qos: int = 2

    @classmethod
    def FromJSON(cls, json: dict):
        return cls(
            topic=json.get("topic", ""),
            function=json.get("function", ""),
            payload_reference=json.get("payload_reference", "")
        )
    
    def toJSON(self) -> dict:
        return dict(
            topic=self.topic,
            function=self.function,
            payload_reference=self.payload_reference
        )

@dataclass
class MQTTConfig:
    broker_url: str
    broker_port: int
    node_name: str
    node_type: str
    max_reconnect_count: int = 5
    reconnect_delay: float = 1
    reconnect_rate: int = 2
    protocol_version: MQTTProtocolVersion = MQTTProtocolVersion.MQTTv5
    callback_api_version: CallbackAPIVersion = CallbackAPIVersion.VERSION2
    subscriptions: List[MQTTSubscription] = field(default_factory=list)

    @classmethod
    def FromJSON(cls, json: dict):
        return cls(
            json["broker_url"],
            json["broker_port"],
            json["node_name"],
            json["node_type"],
            json["max_reconnect_count"],
            json["reconnect_delay"],
            json["reconnect_rate"],
            MQTTProtocolVersion(json["protocol_version"]),
            CallbackAPIVersion(json["callback_api_version"]),
            [MQTTSubscription.FromJSON(s) for s in json["subscriptions"]] if "subscriptions" in json else []
        )
    
    def toJSON(self) -> dict:
        return dict(
            broker_url=self.broker_url,
            broker_port=self.broker_port,
            node_name=self.node_name,
            node_type=self.node_type,
            max_reconnect_count=self.max_reconnect_count,
            reconnect_delay=self.reconnect_delay,
            reconnect_rate=self.reconnect_rate,
            protocol_version=self.protocol_version.value,
            callback_api_version=self.callback_api_version.value,
            subscriptions=[s.toJSON() for s in self.subscriptions]
        )


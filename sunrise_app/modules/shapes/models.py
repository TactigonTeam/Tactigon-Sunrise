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

from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple, Any
from uuid import UUID

from sunrise_app.modules.ros2.models import Ros2ShapeConfig
from sunrise_app.modules.mqtt.models import MQTTConfig


class Severity(Enum):
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3

class MessageType(Enum):
    MESSAGE = "string"
    PROMPT = "prompt"

class ShapesPostAction(Enum):
    READ_TOUCH = 1

@dataclass
class Program:
    state: object
    code: Optional[str] = None

@dataclass
class ShapeConfig:
    id: UUID
    name: str
    created_on: datetime
    modified_on: datetime
    description: Optional[str] = None
    readonly: bool = False
    app_file: str = "program.py"
    ros2_config: Optional[Ros2ShapeConfig] = None
    mqtt_config: Optional[MQTTConfig] = None


    @classmethod
    def FromJSON(cls, json):
        mqtt_config = json.get("mqtt_config", None)
        ros2_config = json.get("ros2_config", None)
        
        return cls(
            id=UUID(json["id"]),
            name=json["name"],
            created_on=datetime.fromisoformat(json["created_on"]),
            modified_on=datetime.fromisoformat(json["modified_on"]),
            description=json["description"],
            readonly=json["readonly"],
            ros2_config=Ros2ShapeConfig.FromJSON(ros2_config) if ros2_config else None,
            mqtt_config=MQTTConfig.FromJSON(mqtt_config) if mqtt_config else None,
        )

    def toJSON(self) -> dict:
        return dict(
            id=self.id.hex,
            name=self.name,
            created_on=self.created_on.isoformat(),
            modified_on=self.modified_on.isoformat(),
            description=self.description,
            readonly=self.readonly,
            ros2_config=self.ros2_config.toJSON() if self.ros2_config else None,
            mqtt_config=self.mqtt_config.toJSON() if self.mqtt_config else None
        )
    
@dataclass
class DebugMessage:
    severity: Severity
    date: datetime
    message: Any
    message_type: MessageType = MessageType.MESSAGE

    @classmethod
    def Debug(cls, message: str):
        return cls(
            Severity.DEBUG,
            datetime.now(),
            message
        )

    @classmethod
    def Info(cls, message: str):
        return cls(
            Severity.INFO,
            datetime.now(),
            message
        )
    
    @classmethod
    def Warning(cls, message: str):
        return cls(
            Severity.WARNING,
            datetime.now(),
            message
        )
    
    @classmethod
    def Error(cls, message: str):
        return cls(
            Severity.ERROR,
            datetime.now(),
            message
        )
    
    @classmethod
    def Prompt(cls, message: Any):
        return cls(
            Severity.DEBUG,
            datetime.now(),
            message,
            MessageType.PROMPT
        )
    
    def toJSON(self) -> dict:
        return dict(
            severity=self.severity.name,
            date=self.date.isoformat(),
            message=self.message if isinstance(self.message, str) else self.message.toJSON(),
            message_type=self.message_type.value
        )

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

from dataclasses import dataclass, field
from enum import Enum

from sunrise_msgs.msg import Action, Intent
from tactigon_gear.models import TSkinConfig

SUNRISE_ACTION_TOPIC = "/sunrise/mission_controller/action"
SUNRISE_INTENT_TOPIC = "/sunrise/mission_controller/intent"

class MappingType(Enum):
    UNDEFINED = ""
    ACTION = "action"
    TEACH_TASK = "teach_task"
    TEACH_SKILL = "teach_skill"
    REPEAT_TASK = "repeat_task"
    REPEAT_SKILL = "repeat_skill"

@dataclass
class GestureMapping:
    gesture: str
    mapping: MappingType

    @classmethod
    def FromJSON(cls, json: dict):
        return cls(
            gesture=json.get("gesture", ""),
            mapping=MappingType(json.get("mapping", ""))
        )
    
    def toJSON(self) -> dict:
        return dict(
            gesture=self.gesture,
            mapping=self.mapping.value
        )
    
@dataclass
class TouchMapping:
    touch: str
    mapping: MappingType

    @classmethod
    def FromJSON(cls, json: dict):
        return cls(
            touch=json.get("touch", ""),
            mapping=MappingType(json.get("mapping", ""))
        )
    
    def toJSON(self) -> dict:
        return dict(
            touch=self.touch,
            mapping=self.mapping.value
        )

@dataclass
class SunriseBridgeConfig:
    tskin_config: TSkinConfig
    intent_topic: str
    action_topic: str
    gestures: list[GestureMapping] = field(default_factory=list)
    touchs: list[TouchMapping] = field(default_factory=list)

    @classmethod
    def FromJSON(cls, json: dict):
        return cls(
            tskin_config=TSkinConfig.FromJSON(json.get("tskin_config", {})),
            intent_topic=json.get("intent_topic", SUNRISE_INTENT_TOPIC),
            action_topic=json.get("action_topic", SUNRISE_ACTION_TOPIC),
            gestures=[GestureMapping.FromJSON(gm) for gm in json.get("gestures", [])],
            touchs=[TouchMapping.FromJSON(gm) for gm in json.get("touchs", [])],
        )
    
    def toJSON(self) -> dict:
        return dict(
            tskin_config=self.tskin_config.toJSON(),
            intent_topic=self.intent_topic,
            action_topic=self.action_topic,
            gestures=[g.toJSON() for g in self.gestures],
            touchs=[t.toJSON() for t in self.touchs],
        )
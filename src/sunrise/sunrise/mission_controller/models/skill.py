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

from typing import Any

class SkillScope(Enum):
    BRACCIO_ROBOT = "braccio_robot"

@dataclass
class Skill:
    scope: SkillScope
    name: str
    payload: Any

    children: list["Skill"] = field(default_factory=list)

    @property
    def has_children(self) -> bool:
        return len(self.children) > 0

    @classmethod
    def FromJSON(cls, json):
        return cls(
            scope=SkillScope(json["scope"]),
            name=json["name"],
            payload=json["payload"],
            children=[Skill.FromJSON(c) for c in json.get("children", [])]
        )
    
    def toJSON(self) -> dict:
        return dict(
            scope=self.scope.value,
            name=self.name,
            payload=self.payload,
            children=self.children
        )
    
@dataclass
class Task:
    name: str
    skills: list[Skill]

    @classmethod
    def FromJSON(cls, json: dict):
        return cls(
            name=json.get("name", ""),
            skills=[Skill.FromJSON(s) for s in json.get("skills", [])]
        )
    
    def toJSON(self) -> dict:
        return dict(
            name=self.name,
            skills=[s.toJSON() for s in self.skills]
        )
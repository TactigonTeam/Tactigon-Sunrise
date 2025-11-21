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

from sunrise.mission_controller.models.skill import Skill

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
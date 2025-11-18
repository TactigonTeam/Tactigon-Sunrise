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

from sunrise.mission_controller.models.skill import Skill, SkillScope

@dataclass
class TEOConfig:
    skills: list[Skill]

    @classmethod
    def FromJSON(cls, json: dict):
        return cls(
            skills=[Skill.FromJSON(skill) for skill in json.get("skills", [])]
        )
    
    def toJSON(self) -> dict:
        return dict(
            skills=[skill.toJSON() for skill in self.skills]
        )
    
    def add_skill(self, skill: Skill, parent: str = "") -> bool:
        if parent:
            return self._add_to_skill(self.skills, skill, parent)
        
        self.skills.append(skill)
        return True
    
    def _add_to_skill(self, skills: list[Skill], skill: Skill, parent: str) -> bool:
        for skill in skills:
            if skill.name == parent:
                skill.children.append(skill)
                return True
            
            if self._add_to_skill(skill.children, skill, parent):
                return True
            
        return False
    
    def get_skill(self, name: str) -> Skill | None:
        return next((skill for skill in self.skills if skill.name == name), None)
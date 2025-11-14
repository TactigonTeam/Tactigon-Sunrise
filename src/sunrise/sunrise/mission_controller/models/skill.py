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
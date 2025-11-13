from dataclasses import dataclass
from enum import Enum

from typing import Any

from sunrise.sunrise.models.mission_controller import MissionControllerConfig

@dataclass
class SunriseConfig:
    mission_controller: MissionControllerConfig
    teacher_config_path: str
    student_config_path: str

    @classmethod
    def FromJSON(cls, json: dict):
        return cls(
            mission_controller=MissionControllerConfig.FromJSON(json.get("mission_controller", {})),
            teacher_config_path=json.get("teacher_config_path", ""),
            student_config_path=json.get("student_config_path", ""),
        )
    
    def toJSON(self) -> dict:
        return dict(
            node=self.mission_controller.toJSON(),
            teacher_config_path=self.teacher_config_path,
            student_config_path=self.student_config_path,
        )
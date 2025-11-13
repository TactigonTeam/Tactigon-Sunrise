import json
from sunrise.sunrise.teacher.models import TeacherConfig
from sunrise.sunrise.models.skill import Skill


class Teacher():
    _config: TeacherConfig

    def __init__(self, config_path: str):
        self._config = self.load_config(config_path)

    def load_config(self, config_path: str) -> TeacherConfig:
        with open(config_path) as cf:
            return TeacherConfig.FromJSON(json.load(cf))

    def add_skill(self, skill: Skill, parent: str = ""):
        self._config.add_skill(skill, parent)

    def get_skill(self, name: str) -> Skill | None:
        return self._config.get_skill(name)
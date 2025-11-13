import json

from sunrise.sunrise.student.models import StudentConfig

class Student:
    _config: StudentConfig

    def __init__(self, config_path: str):
        self._config = self.load_config(config_path)

    def load_config(self, config_path: str) -> StudentConfig:
        with open(config_path) as cf:
            return StudentConfig.FromJSON(json.load(cf))

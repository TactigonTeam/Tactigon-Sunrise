import json

from sunrise.mission_controller.leo.models import LEOConfig

class LEO:
    _config: LEOConfig

    def __init__(self, config_path: str):
        self._config = self.load_config(config_path)

    def load_config(self, config_path: str) -> LEOConfig:
        with open(config_path) as cf:
            return LEOConfig.FromJSON(json.load(cf))

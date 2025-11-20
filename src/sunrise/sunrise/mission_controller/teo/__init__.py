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

import json
from sunrise.mission_controller.teo.models import TEOConfig
from sunrise.mission_controller.models.skill import Skill, Task


class TEO():
    _config_path: str
    _config: TEOConfig
    _task: Task | None

    def __init__(self, config_path: str):
        self._config_path = config_path
        self._config = self.load_config(config_path)
        self._task = None

    def load_config(self, config_path: str) -> TEOConfig:
        with open(config_path) as cf:
            return TEOConfig.FromJSON(json.load(cf))
        
    def save_config(self):
        with open(self._config_path, "w") as cf:
            json.dump(self._config.toJSON(), cf, indent=4)

    def add_task(self, task_name: str) -> Task:
        return self._config.add_task(task_name)

    def add_skill(self, task_name: str, skill: Skill, parent: str = ""):
        if not self._task:
            self._task = Task("task", [])

        self._config.add_skill(task_name, skill, parent)

    def get_task(self, name: str) -> Task | None:
        return self._config.get_task(name)
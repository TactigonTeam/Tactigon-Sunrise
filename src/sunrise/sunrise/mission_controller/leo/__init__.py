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

from sunrise.mission_controller.leo.models import LEOConfig

class LEO:
    _config: LEOConfig

    def __init__(self, config_path: str):
        self._config = self.load_config(config_path)

    def load_config(self, config_path: str) -> LEOConfig:
        with open(config_path) as cf:
            return LEOConfig.FromJSON(json.load(cf))

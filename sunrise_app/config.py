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
#********************************************************************************/

import json
from functools import wraps
from os import path
from flask import redirect, url_for

from sunrise_app.models import BASE_PATH, AppConfig

config_file_path = path.join(BASE_PATH, "config")
config_file = path.join(config_file_path, "config.json")

if path.exists(config_file_path) and path.exists(config_file):
    with open(config_file, "r") as cf:
        app_config = AppConfig.FromJSON(json.load(cf), config_file)
else:
    app_config = AppConfig.Default(config_file)
    app_config.save()
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

import sys
import json
from os import getcwd
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, List

from tactigon_gear import  __version__ as tactigon_gear_version

BASE_PATH = getcwd()

@dataclass
class AppConfig(object):
    DEBUG: bool
    SECRET_KEY: str
    SEND_FILE_MAX_AGE_DEFAULT: int = 1
    file_path: Optional[str] = None

    @classmethod
    def Default(cls, file_path):
        return cls(
            DEBUG=True,
            SECRET_KEY="change-me",
            file_path=file_path
        )

    @classmethod
    def FromFile(cls, file_path):
        with open(file_path, "r") as config_file:
            return cls.FromJSON(json.load(config_file), file_path)

    @classmethod
    def FromJSON(cls, json: dict, file_path: str):
        return cls(
            json["DEBUG"],
            json["SECRET_KEY"],
            json["SEND_FILE_MAX_AGE_DEFAULT"],
            file_path
            )
    
    def toJSON(self) -> object:
        return {
            "DEBUG": self.DEBUG,
            "SECRET_KEY": self.SECRET_KEY,
            "SEND_FILE_MAX_AGE_DEFAULT": self.SEND_FILE_MAX_AGE_DEFAULT,
        }
    
    def save(self):
        if self.file_path:
            with open(self.file_path, "w") as config_file:
                json.dump(self.toJSON(), config_file, indent=2)
        
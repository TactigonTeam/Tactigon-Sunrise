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

from tactigon_gear.tskin_socket import TSkinConfig, SocketConfig
from tactigon_gear.models.audio import TSpeechObject

@dataclass
class TactigonConfig:
    tskin_config: TSkinConfig
    socket_config: SocketConfig
    speech: TSpeechObject | None = None

    @classmethod
    def FromJSON(cls, json: dict):
        return cls(
            tskin_config=TSkinConfig.FromJSON(json.get("tskin_config", {})),
            socket_config=SocketConfig.FromJSON(json.get("socket_config", {})),
            speech=TSpeechObject.FromJSON(json.get("speech", {}))
        )
    
    def toJSON(self) -> dict:
        return dict(
            tskin_config=self.tskin_config.toJSON(),
            socket_config=self.socket_config.toJSON(),
            speech=self.speech.toJSON() if self.speech else None,
        )
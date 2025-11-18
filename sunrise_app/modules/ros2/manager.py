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

from flask import current_app

from typing import Optional

from sunrise_app.modules.ros2.extension import Ros2Interface

def get_ros2_interface() -> Optional[Ros2Interface]:
    if Ros2Interface.__name__ in current_app.extensions and isinstance(current_app.extensions[Ros2Interface.__name__], Ros2Interface):
        return current_app.extensions[Ros2Interface.__name__]
    
    return None
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

from flask import current_app

from typing import Optional

from sunrise_app.modules.zion.extension import ZionInterface

def get_zion_interface() -> Optional[ZionInterface]:
    if ZionInterface.__name__ in current_app.extensions and isinstance(current_app.extensions[ZionInterface.__name__], ZionInterface):
        return current_app.extensions[ZionInterface.__name__]
    
    return None
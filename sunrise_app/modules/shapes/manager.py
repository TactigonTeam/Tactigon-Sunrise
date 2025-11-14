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

from sunrise_app.modules.shapes.extension import ShapesApp

def get_shapes_app() -> Optional[ShapesApp]:
    if ShapesApp.__name__ in current_app.extensions and isinstance(current_app.extensions[ShapesApp.__name__], ShapesApp):
        return current_app.extensions[ShapesApp.__name__]
    
    return None
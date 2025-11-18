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

from flask import request, flash
from typing import Any, Optional


def get_from_request(name: str) -> Optional[str]:
    if name in request.args:
        return request.args.get(name)
    
    if name in request.form:
        return request.form.get(name)
    
    return None

def check_empty_inputs(local_variables: Any) -> bool:
    for var_name, var_value in local_variables:
        if not var_name.startswith('_') and (var_value is None or var_value == ""):
            flash(f"{var_name.replace('_', ' ')} is required!", category="danger")
            return True

    return False
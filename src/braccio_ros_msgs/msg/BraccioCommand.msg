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

# Target Cartesian coordinates
int16 x
int16 y
int16 z

# Target wrist orientation
# Use strings "HORIZONTAL" or "VERTICAL"
string wrist_state

# Target gripper state
# Use strings "OPEN" or "CLOSE"
string gripper_state
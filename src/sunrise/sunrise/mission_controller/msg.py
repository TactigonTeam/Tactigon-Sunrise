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

from std_msgs.msg import String, Int64, Float64, Bool
from rcl_interfaces.msg import Log
from sunrise_msgs.msg import Action, Intent, Point2D, Marker, MarkerList
from braccio_ros_msgs.msg import BraccioCommand, BraccioResponse, BraccioJointCommand
from comau_msgs.msg import ActionResult, JointPose

StdMessageTypes = String | Int64 | Bool | Float64
InterfaceMessageTypes = Log
SunriseMessageTypes = Action | Intent | Point2D | Marker | MarkerList
BraccioMessageTypes = BraccioCommand | BraccioResponse | BraccioJointCommand | ActionResult | JointPose
RosMessageTypes = StdMessageTypes | InterfaceMessageTypes | SunriseMessageTypes | BraccioMessageTypes

def get_message_type_by_name(name: str) -> RosMessageTypes:
    type_index = [t.__name__ for t in RosMessageTypes.__args__].index(name)
    
    if type_index == -1:
        return String # type: ignore
    
    return RosMessageTypes.__args__[type_index]

def get_message_name() -> list[str]:
    return [t.__name__ for t in RosMessageTypes.__args__]

def get_message_data(msg: RosMessageTypes) -> dict:
    data = {}
    for field in msg.get_fields_and_field_types():
        data[field] = getattr(msg, field)
    return data
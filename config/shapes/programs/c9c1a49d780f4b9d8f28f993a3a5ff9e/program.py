
# Shapes by Next Industries

import time
import random
import types
import json
from numbers import Number
from datetime import datetime
from std_msgs.msg import String, Bool, Byte, Char, Float64, Int64, UInt64, ColorRGBA
from sunrise_msgs.msg import Action, Intent, Point2D, Marker, MarkerList, BraccioCommand, BraccioResponse
from sunrise_app.modules.shapes.extension import ShapesPostAction, LoggingQueue
from sunrise_app.modules.zion.extension import ZionInterface, Scope, AlarmSearchStatus, AlarmSeverity
from sunrise_app.modules.ros2.extension import Ros2Interface
from sunrise_app.modules.ros2.models import RosMessageTypes
from sunrise_app.modules.mqtt.extension import MQTTClient
from typing import List, Optional, Union, Any

def zion_device_last_telemetry(zion: Optional[ZionInterface], device_id: str, keys: str) -> dict:
    if not zion:
        return {}
    
    data = zion.device_last_telemetry(device_id, keys)

    if not data:
        return {}

    return data

def zion_device_attr(zion: Optional[ZionInterface], device_id: str, scope: Scope, keys: str) -> dict:
    if not zion:
        return {}
    
    data = zion.device_attr(device_id, scope, keys)

    if not data:
        return {}

    return data

def zion_device_alarm(zion: Optional[ZionInterface], device_id: str, severity: AlarmSeverity, search_status: AlarmSearchStatus) -> List[dict]:
    if not zion:
        return []
    
    data = zion.device_alarm(device_id, severity, search_status)

    if not data:
        return []

    return data

def zion_send_device_last_telemetry(zion: Optional[ZionInterface], device_id: str, key: str, data) -> bool:
    if not zion:
        return False

    payload = {}
    payload[key] = data

    return zion.send_device_last_telemetry(device_id, payload)

def zion_delete_device_attr(zion: Optional[ZionInterface], device_id: str, scope: Scope, keys: str) -> bool:
    if not zion:
        return False

    return zion.delete_device_attr(device_id, scope, keys)

def zion_send_device_attr(zion: Optional[ZionInterface], device_id: str, scope: Scope, key: str, data) -> bool:
    if not zion:
        return False

    payload = {}
    payload[key] = data

    return zion.send_device_attr(device_id, payload, scope)    

def zion_send_device_alarm(zion: Optional[ZionInterface], device_id: str, name: str) -> bool:
    if not zion:
        return False

    return zion.upsert_device_alarm(device_id, name, name) 

def debug(logging_queue: LoggingQueue, msg: Optional[Any]):

    if isinstance(msg,(float)):
        rounded=round(msg,4)
        logging_queue.debug(str(rounded))
    elif isinstance(msg, types.GeneratorType):
        for line in msg:
            logging_queue.prompt(line)
    else:
        logging_queue.debug(str(msg).replace("\n","<br>"))

def ros2_run(ros2: Optional[Ros2Interface], command: str):
    if not ros2:
        return

    ros2.run(command)

def ros2_publish(ros2: Optional[Ros2Interface], topic: str, message: RosMessageTypes):
    if not ros2:
        return
    
    ros2.publish(topic, message)

def mqtt_publish(mqtt: Optional[MQTTClient], topic: str, payload: Any):
    if not mqtt:
        return
    
    mqtt.publish(topic, payload)


# ---------- Generated code ---------------

tactigon_intent = None
log = None
create_intent = None


def _sunrise_app_bridge_intent(logging_queue: LoggingQueue):
    global pointing, markers, log, create_action, payload, tactigon_intent, create_intent, x, marker_id, marker_map, intent, intent_map
    if tactigon_intent.get('type', None) == 1:
        debug(logging_queue, 'Create a repear intent')
        create_intent = Intent(type=Intent.REPEAT, payload=json.dumps({'task': 'pick task for robot'}))

def sunrise_app_setup(
        zion: Optional[ZionInterface],
        ros2: Optional[Ros2Interface],
        mqtt: Optional[MQTTClient],
        logging_queue: LoggingQueue):

    global pointing, markers, log, create_action, payload, tactigon_intent, create_intent, x, marker_id, marker_map, intent, intent_map
    create_intent = None

def sunrise_app_close(
        zion: Optional[ZionInterface],
        ros2: Optional[Ros2Interface],
        mqtt: Optional[MQTTClient],
        logging_queue: LoggingQueue):

    global pointing, markers, log, create_action, payload, tactigon_intent, create_intent, x, marker_id, marker_map, intent, intent_map
    pass

def sunrise_app_function(
        zion: Optional[ZionInterface],
        ros2: Optional[Ros2Interface],
        mqtt: Optional[MQTTClient],
        logging_queue: LoggingQueue):

    global pointing, markers, log, create_action, payload, tactigon_intent, create_intent, x, marker_id, marker_map, intent, intent_map
    if create_intent != None:
        ros2_publish(ros2, '/sunrise/mission_controller/intent', create_intent)
        create_intent = None


def _sunrise_mission_controller_log(logging_queue: LoggingQueue):
    global pointing, markers, log, create_action, payload, tactigon_intent, create_intent, x, marker_id, marker_map, intent, intent_map
    debug(logging_queue, log)

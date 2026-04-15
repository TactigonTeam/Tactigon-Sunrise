function loadCustomBlocks(response) {
    const zion = response ? response.zion : [];
    const ros2 = response ? response.ros2 : {};
    
    loadZionBlocks(zion);
    loadRos2Blocks(ros2);
    loadMQTTBlocks();
    loadDictionaryBlocks();

    const blocksDefinitions = Blockly.common.createBlockDefinitionsFromJsonArray([
        {
            "type": "sunrise_app_function",
            "message0": "Loop %1 do %2",
            "args0": [
                {
                    "type": "input_dummy",
                    "name": ""
                },
                {
                    "type": "input_statement",
                    "name": "BODY"
                }
            ],
            "colour": 230,
            "tooltip": "Main function",
            "helpUrl": ""
        },
        {
            "type": "sunrise_app_setup",
            "message0": "Setup %1 do %2",
            "args0": [
                {
                    "type": "input_dummy",
                    "name": ""
                },
                {
                    "type": "input_statement",
                    "name": "setup_code"
                }
            ],
            "inputsInline": false,
            "colour": 230,
            "tooltip": "Setup function",
            "helpUrl": ""
        },
        {
            "type": "sunrise_app_close",
            "message0": "Close %1 do %2",
            "args0": [
                {
                    "type": "input_dummy",
                    "name": ""
                },
                {
                    "type": "input_statement",
                    "name": "setup_code"
                }
            ],
            "inputsInline": false,
            "colour": 230,
            "tooltip": "Setup function",
            "helpUrl": ""
        },
        {
            "type": "sunrise_app_debug",
            "message0": "Debug %1",
            "args0": [
                {
                    "type": "input_value",
                    "name": "TEXT"
                }
            ],
            "previousStatement": null,
            "nextStatement": null,
            "colour": "#bce261",
            "tooltip": "Send a message to the terminal",
            "helpUrl": ""
        }
    ]);
    Blockly.common.defineBlocks(blocksDefinitions);
}

function loadDictionaryBlocks(){
    const blocksDefinitions = Blockly.common.createBlockDefinitionsFromJsonArray([
        {
            "type": "get_dict_property",
            "message0": "Get item %1 from dictionary %2",
            "args0": [
                {
                "type": "input_value",
                "name": "key",
                "check": "String"
                },
                {
                "type": "input_value",
                "name": "dictionary"
                }
            ],
            "output": null,
            "colour": '#636363',
            "tooltip": "Get the value for a key in a dictionary",
            "helpUrl": "",
            "inputsInline": true
        },
        {
            "type": "dict_builder",
            "message0": "Create map %1",
            "args0": [
                {
                    "type": "input_statement",
                    "name": "PAIRS"
                }
            ],
            "output": "Dict",
            "colour": 230,
            "tooltip": "Create a dictionary",
        },
        {
            "type": "dict_pair",
            "message0": "Key %1 value %2",
            "args0": [
                {
                    "type": "input_value",
                    "name": "dict_key",
                    "check": "String"
                },
                {
                    "type": "input_value",
                    "name": "dict_value"
                }
            ],
            "previousStatement": null,
            "nextStatement": null,
            "colour": 200,
            "tooltip": "Create a key-value pair for a dictionary",
        },
        {
            "type": "dict_to_json",
            "message0": "jsonify %1",
            "args0": [
                {
                    "type": "input_value",
                    "name": "dict",
                    "check": "Dict"
                }
            ],
            "output": "JSONString",
            "colour": 200,
            "tooltip": "Convert dictionary into json string",
            "inputsInline": true
        },
        {
            "type": "json_to_dict",
            "message0": "Dict from json %1",
            "args0": [
                {
                    "type": "input_value",
                    "name": "json",
                    "check": "String"
                }
            ],
            "output": "Dict",
            "colour": 200,
            "tooltip": "Convert json string into dictionary",
            "inputsInline": true
        }
    ]);

    Blockly.common.defineBlocks(blocksDefinitions);
}

function loadZionBlocks(zion){
    Blockly.Blocks['device_list'] = {
        init: function () {
            this.jsonInit({
                "type": "device_list",
                "message0": "Device %1",
                "args0": [
                    {
                        "type": "field_dropdown",
                        "name": "device",
                        "options": zion.devices
                    }
                ],
                "output": "ZionDevice",
                "colour": "#EB6152",
                "tooltip": "Devices from Zion",
                "helpUrl": ""
            });
        }
    };

    Blockly.Blocks['scope_list'] = {
        init: function () {
            this.jsonInit({
                "type": "scope_list",
                "message0": "Scope %1",
                "args0": [
                    {
                        "type": "field_dropdown",
                        "name": "scope",
                        "options": zion.scopes
                    }
                ],
                "output": "ZionScope",
                "colour": "#EB6152",
                "tooltip": "Attribute scope from Zion",
                "helpUrl": ""
            });
        }
    };

    Blockly.Blocks['alarm_severity_list'] = {
        init: function () {
            this.jsonInit({
                "type": "alarm_severity_list",
                "message0": "Alarm severity %1",
                "args0": [
                    {
                        "type": "field_dropdown",
                        "name": "severity",
                        "options": zion.alarmSeverity
                    }
                ],
                "output": "ZionAlarmSeverity",
                "colour": "#EB6152",
                "tooltip": "Alarm severity from Zion",
                "helpUrl": ""
            });
        }
    };

    Blockly.Blocks['alarm_search_status_list'] = {
        init: function () {
            this.jsonInit({
                "type": "alarm_search_status_list",
                "message0": "Alarm search status %1",
                "args0": [
                    {
                        "type": "field_dropdown",
                        "name": "search_status",
                        "options": zion.alarmSearchStatus
                    }
                ],
                "output": "ZionAlarmSeachStatus",
                "colour": "#EB6152",
                "tooltip": "Alarm search status from Zion",
                "helpUrl": ""
            });
        }
    };

    Blockly.Blocks['delete_device_attr'] = {
        init: function () {
            this.jsonInit({
                "type": "delete_device_attr",
                "tooltip": "delete attribute from device",
                "helpUrl": "",
                "message0": "Delete Attribute from device: %1 Scope %2 Key %3",
                "args0": [          
                    {
                        "type": "input_value",
                        "name": "device",
                        "check": "ZionDevice"
                    },
                    {
                        "type": "input_value",
                        "name": "scope",
                        "check": "ZionScope"
                    },
                    {
                        "type": "input_value",
                        "name": "key",
                        "check": "String"
                    }
                ],
                "output": "Dictionary",
                "colour": '#6665DD'

            });
        }
    };

    Blockly.Blocks['device_last_telemetry'] = {
        init: function () {
            this.jsonInit({
                "type": "device_last_telemetry",
                "message0": "Get device last telemetry %1 (Optional) filter key %2",
                "args0": [
                    {
                        "type": "input_value",
                        "name": "device",
                        "check": "ZionDevice"
                    },
                    {
                        "type": "input_value",
                        "name": "keys",
                        "check": "String"
                    }
                ],
                "output": "Dictionary",
                "colour": '#6665DD',
                "tooltip": "Get last telemetry from device",
                "helpUrl": ""
            });
        }
    };

    Blockly.Blocks['device_attr'] = {
        init: function () {
            this.jsonInit({
                "type": "device_attr",
                "message0": "Get device attribute %1 Scope %2 (Optional) filter key %3",
                "args0": [
                    {
                        "type": "input_value",
                        "name": "device",
                        "check": "ZionDevice"
                    },
                    {
                        "type": "input_value",
                        "name": "scope",
                        "check": "ZionScope"
                    },
                    {
                        "type": "input_value",
                        "name": "keys",
                        "check": "String"
                    }
                ],
                "output": "Dictionary",
                "colour": '#6665DD',
                "tooltip": "Get last telemetry from device",
                "helpUrl": ""
            });
        }
    };

    Blockly.Blocks['device_alarm'] = {
        init: function () {
            this.jsonInit({
                "type": "device_alarm",
                "message0": "Get device alarm %1 Severity %2 Search status %3",
                "args0": [
                    {
                        "type": "input_value",
                        "name": "device",
                        "check": "ZionDevice"
                    },
                    {
                        "type": "input_value",
                        "name": "severity",
                        "check": "ZionAlarmSeverity"
                    },
                    {
                        "type": "input_value",
                        "name": "search_status",
                        "check": "ZionAlarmSeachStatus"
                    }
                ],
                "output": "Array",
                "colour": '#6665DD',
                "tooltip": "Get last telemetry from device",
                "helpUrl": ""
            });
        }
    };

    Blockly.Blocks['send_device_last_telemetry'] = {
        init: function () {
            this.jsonInit({
                "type": "send_device_last_telemetry",
                "message0": "Update telemetry %1 Key %2 Value %3",
                "args0": [
                    {
                        "type": "input_value",
                        "name": "device",
                        "check": "ZionDevice"
                    },
                    {
                        "type": "input_value",
                        "name": "key",
                        "check": "String"
                    },
                    {
                        "type": "input_value",
                        "name": "payload",
                    }
                ],
                "output": "Boolean",
                "colour": '#6665DD',
                "tooltip": "Send telemetry to device",
                "helpUrl": ""
            });
        }
    };

    Blockly.Blocks['send_device_attr'] = {
        init: function () {
            this.jsonInit({
                "type": "send_device_last_telemetry",
                "message0": "Update attribute of device %1 Scope %2 Key %3 Value %4",
                "args0": [
                    {
                        "type": "input_value",
                        "name": "device",
                        "check": "ZionDevice"
                    },
                    {
                        "type": "input_value",
                        "name": "scope",
                        "check": "ZionScope"
                    },
                    {
                        "type": "input_value",
                        "name": "key",
                        "check": "String"
                    },
                    {
                        "type": "input_value",
                        "name": "payload",
                    }
                ],
                "output": "Boolean",
                "colour": '#6665DD',
                "tooltip": "Send attribute to device",
                "helpUrl": ""
            });
        }
    };
    
    Blockly.Blocks['send_device_alarm'] = {
        init: function () {
            this.jsonInit({
                "type": "send_device_last_telemetry",
                "message0": "Create or update alarm on device %1 alarm %2",
                "args0": [
                    {
                        "type": "input_value",
                        "name": "device",
                        "check": "ZionDevice"
                    },
                    {
                        "type": "input_value",
                        "name": "name",
                        "check": "String"
                    }
                ],
                "output": "Boolean",
                "colour": '#6665DD',
                "tooltip": "Create or update alarm on device",
                "helpUrl": ""
            });
        }
    };
} 

function loadRos2Blocks(ros2blocks){
    const blocksDefinitions = Blockly.common.createBlockDefinitionsFromJsonArray([
        {
            "type": "ros2_command",
            "message0": "ros2 run %1",
            "args0": [
                {
                    "type": "field_dropdown",
                    "name": "command",
                    "options": ros2blocks.commands
                }
            ],
            "previousStatement": null,
            "nextStatement": null,
            "tooltip": "Start a ROS 2 process",
            "helpUrl": "",
            "colour": 225
        },
        {
            "type": "ros2_subscribe",
            "message0": "On topic %1 type %2 get values in %3",
            "args0": [
                {
                    "type": "input_value",
                    "name": "topic",
                    "check": "String"
                },
                {
                    "type": "input_value",
                    "name": "message_type",
                    "check": "GenericRos2MessageType"
                },
                {
                    "type": "field_variable",
                    "name": "var_name",
                    "variable": "payload"
                }
            ],
            "message1": "do %1",
            "args1": [
                {
                    "type": "input_statement",
                    "name": "function"
                }
            ],
            "tooltip": "Subscribe to a ROS 2 topic and trigger the call on message event",
            "helpUrl": "",
            "colour": 225
        },
        {
            "type": "ros2_message_type",
            "message0": "Type %1",
            "args0": [
                {
                "type": "field_dropdown",
                "name": "message_type",
                "options": ros2blocks.default_types
                }
            ],
            "output": "GenericRos2MessageType",
            "tooltip": "Select a ROS 2 message type",
            "helpUrl": "",
            "colour": 225
        },
        {
            "type": "ros2_publish",
            "message0": "Publish message %1 on topic %2",
            "args0": [
                {
                    "type": "input_value",
                    "name": "message_type",
                    "check": "Ros2MessageType"
                },
                {
                    "type": "input_value",
                    "name": "topic",
                    "check": "String"
                }                
            ],
            "tooltip": "Publish a message to a ROS 2 topic",
            "helpUrl": "",
            "previousStatement": null,
            "nextStatement": null,
            "colour": 225
        },
        {
            "type": "ros2_message_String",
            "message0": "String(data=%1)",
            "args0": [
                {
                    "type": "input_value",
                    "name": "data",
                    "check": "String"
                }
            ],
            "output": "Ros2MessageType",
            "tooltip": "Create a ROS 2 String message",
            "helpUrl": "",
            "colour": 225
        },
        {
            "type": "ros2_message_Bool",
            "message0": "Bool(data=%1)",
            "args0": [
                {
                    "type": "input_value",
                    "name": "data",
                    "check": "Boolean"
                }
            ],
            "output": "Ros2MessageType",
            "tooltip": "Create a ROS 2 Bool message",
            "helpUrl": "",
            "colour": 225
        },
        {
            "type": "ros2_message_Int64",
            "message0": "Int64(data=%1)",
            "args0": [
                {
                    "type": "input_value",
                    "name": "data",
                    "check": "Number"
                }
            ],
            "output": "Ros2MessageType",
            "tooltip": "Create a ROS 2 Int64 message",
            "helpUrl": "",
            "colour": 225
        },
        {
            "type": "ros2_message_Float64",
            "message0": "Float64(data=%1)",
            "args0": [
                {
                    "type": "input_value",
                    "name": "data",
                    "check": "Number"
                }
            ],
            "output": "Ros2MessageType",
            "tooltip": "Create a ROS 2 Float64 message",
            "helpUrl": "",
            "colour": 225
        },
        {
            "type": "ros2_message_Action_type",
            "message0": "Action type %1",
            "args0": [
                {
                    "type": "field_dropdown",
                    "name": "type",
                    "options": ros2blocks.action_types
                }
            ],
            "output": "Ros2ActionType",
            "tooltip": "Select a ROS 2 message type",
            "helpUrl": "",
            "colour": 225
        },
        {
            "type": "ros2_message_Action",
            "message0": "Action(type=%1, payload=%2)",
            "args0": [
                {
                    "type": "input_value",
                    "name": "type",
                    "check": "Ros2ActionType"
                },
                {
                    "type": "input_value",
                    "name": "payload",
                    "check": "JSONString"
                }
            ],
            "output": "Ros2MessageType",
            "tooltip": "Create a ROS 2 Float64 message",
            "helpUrl": "",
            "colour": 225
        },
        {
            "type": "ros2_message_Intent_type",
            "message0": "Intent type %1",
            "args0": [
                {
                    "type": "field_dropdown",
                    "name": "type",
                    "options": ros2blocks.intent_types
                }
            ],
            "output": "Ros2IntentType",
            "tooltip": "Select a ROS 2 message type",
            "helpUrl": "",
            "colour": 225
        },
        {
            "type": "ros2_message_Intent",
            "message0": "Intent(type=%1, payload=%2)",
            "args0": [
                {
                    "type": "input_value",
                    "name": "type",
                    "check": "Ros2IntentType"
                },
                {
                    "type": "input_value",
                    "name": "payload",
                    "check": "JSONString"
                }
            ],
            "output": "Ros2MessageType",
            "tooltip": "Create a ROS 2 Float64 message",
            "helpUrl": "",
            "colour": 225
        },
        {
            "type": "ros2_message_Point2D",
            "message0": "Point2D(x=%1, y=%2)",
            "args0": [
                {
                    "type": "input_value",
                    "name": "x",
                    "check": "Number"
                },
                {
                    "type": "input_value",
                    "name": "y",
                    "check": "Number"
                }
            ],
            "output": "Ros2Point2DType",
            "tooltip": "Create a ROS 2 Point2D message",
            "helpUrl": "",
            "colour": 225
        },
        {
            "type": "ros2_message_Marker",
            "message0": "Marker",
            "message1": "id=%1",
            "message2": "p1=%1",
            "message3": "p2=%1",
            "message4": "p3=%1",
            "message5": "p4=%1",
            "args1": [
                {
                    "type": "input_value",
                    "name": "marker_id",
                    "check": "Number"
                }
            ],
            "args2": [
                {
                    "type": "input_value",
                    "name": "p1",
                    "check": "Ros2Point2DType"
                }
            ],
            "args3": [
                {
                    "type": "input_value",
                    "name": "p2",
                    "check": "Ros2Point2DType"
                }
            ],
            "args4": [
                {
                    "type": "input_value",
                    "name": "p3",
                    "check": "Ros2Point2DType"
                }
            ],
            "args5": [
                {
                    "type": "input_value",
                    "name": "p4",
                    "check": "Ros2Point2DType"
                }
            ],
            "output": "Ros2MessageType",
            "tooltip": "Create a ROS 2 Marker message",
            "helpUrl": "",
            "colour": 225
        },
    ]);

    Blockly.common.defineBlocks(blocksDefinitions);
}

function loadMQTTBlocks(){
    const blocksDefinitions = Blockly.common.createBlockDefinitionsFromJsonArray([
        {
            "type": "mqtt_subscribe",
            "message0": "On message from %1 get values in %2",
            "args0": [
                {
                    "type": "input_value",
                    "name": "topic",
                    "check": "String"
                },
                {
                    "type": "field_variable",
                    "name": "var_name",
                    "variable": "payload"
                }
            ],
            "message1": "do %1",
            "args1": [
                {
                    "type": "input_statement",
                    "name": "function"
                }
            ],
            "tooltip": "Subscribe to a topic and trigger the call on message event",
            "helpUrl": "",
            "colour": 225
        },
        {
            "type": "mqtt_publish",

            "message0": "publish payload %1 on topic %2",
            "args0": [
                {
                    "type": "input_value",
                    "name": "payload"
                },
                {
                    "type": "input_value",
                    "name": "topic",
                    "check": "String"
                }
            ],
            "tooltip": "publish a message to a topic",
            "helpUrl": "",
            "previousStatement": null,
            "nextStatement": null,
            "colour": 225
        }
    ]);

    Blockly.common.defineBlocks(blocksDefinitions);

}

function defineImportsAndLibraries(){
    return `
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
        logging_queue.debug(str(msg).replace("\\n","<br>"))

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

`;
}

function defineCustomGenerators() {
    Blockly.Python.INDENT = '    ';

    python.pythonGenerator.forBlock['sunrise_app_setup'] = function (block, generator) {
        var statements_body = Blockly.Python.statementToCode(block, 'setup_code');
        
        if (!statements_body) {
            statements_body = Blockly.Python.INDENT + "pass\n"
        }

        let variables = block.workspace.getAllVariables().map((v) => {
            return v.name;
        }).join(', ');

        if (variables.length > 0){
            variables = `${Blockly.Python.INDENT}global ${variables}\n`;
        }

        var code = 'def sunrise_app_setup(\n' +
            Blockly.Python.INDENT + Blockly.Python.INDENT + 'zion: Optional[ZionInterface],\n' +
            Blockly.Python.INDENT + Blockly.Python.INDENT + 'ros2: Optional[Ros2Interface],\n' +
            Blockly.Python.INDENT + Blockly.Python.INDENT + 'mqtt: Optional[MQTTClient],\n' +
            Blockly.Python.INDENT + Blockly.Python.INDENT + 'logging_queue: LoggingQueue):\n\n' +
            variables +
            statements_body;
        return code;
    };

    python.pythonGenerator.forBlock['sunrise_app_close'] = function (block, generator) {
        var statements_body = Blockly.Python.statementToCode(block, 'setup_code');
        
        if (!statements_body) {
            statements_body = Blockly.Python.INDENT + "pass\n"
        }

        let variables = block.workspace.getAllVariables().map((v) => {
            return v.name;
        }).join(', ');

        if (variables.length > 0){
            variables = `${Blockly.Python.INDENT}global ${variables}\n`;
        }

        var code = 'def sunrise_app_close(\n' +
            Blockly.Python.INDENT + Blockly.Python.INDENT + 'zion: Optional[ZionInterface],\n' +
            Blockly.Python.INDENT + Blockly.Python.INDENT + 'ros2: Optional[Ros2Interface],\n' +
            Blockly.Python.INDENT + Blockly.Python.INDENT + 'mqtt: Optional[MQTTClient],\n' +
            Blockly.Python.INDENT + Blockly.Python.INDENT + 'logging_queue: LoggingQueue):\n\n' +
            variables +
            statements_body;
        return code;
    };

    python.pythonGenerator.forBlock['sunrise_app_function'] = function (block, generator) {
        var statements_body = Blockly.Python.statementToCode(block, 'BODY');
        
        if (!statements_body) {
            statements_body = Blockly.Python.INDENT + "pass\n"
        }

        let variables = block.workspace.getAllVariables().map((v) => {
            return v.name;
        }).join(', ');

        if (variables.length > 0){
            variables = `${Blockly.Python.INDENT}global ${variables}\n`;
        }

        var code = 'def sunrise_app_function(\n' +
            Blockly.Python.INDENT + Blockly.Python.INDENT + 'zion: Optional[ZionInterface],\n' +
            Blockly.Python.INDENT + Blockly.Python.INDENT + 'ros2: Optional[Ros2Interface],\n' +
            Blockly.Python.INDENT + Blockly.Python.INDENT + 'mqtt: Optional[MQTTClient],\n' +
            Blockly.Python.INDENT + Blockly.Python.INDENT + 'logging_queue: LoggingQueue):\n\n' +
            variables +
            statements_body + '\n';
        return code;
    };

    python.pythonGenerator.forBlock['sunrise_app_debug'] = function (block, generator) {
        var message = generator.valueToCode(block, 'TEXT', python.Order.ATOMIC);
        var code = `debug(logging_queue, ${message})\n`;
        return code;
    };
    
    defineDictionaryGenerators();
    defineZionGenerators();
    defineRos2Generators();
    defineMQTTGenerators();
}

function defineDictionaryGenerators() {
    python.pythonGenerator.forBlock['get_dict_property'] = function (block, generator) {
        const dict = Blockly.Python.valueToCode(block, 'dictionary', Blockly.Python.ORDER_ATOMIC) || "{}";
        const key = Blockly.Python.valueToCode(block, 'key', Blockly.Python.ORDER_ATOMIC) || "''";

        const code = `${dict}.get(${key}, None)`;
        return [code, Blockly.Python.ORDER_ATOMIC];
    };

    python.pythonGenerator.forBlock['dict_builder'] = function(block) {
        const pairBlock = block.getInputTargetBlock('PAIRS');
        const pairCode = Blockly.Python.blockToCode(pairBlock).slice(0, -2); // remove trailing comma and space
        const code = "{" + pairCode + "}";

        return [code, Blockly.Python.ORDER_ATOMIC];
    };

    python.pythonGenerator.forBlock['dict_pair'] = function (block) {
        const key = Blockly.Python.valueToCode(block, 'dict_key', Blockly.Python.ORDER_ATOMIC) || "'data'";
        const value = Blockly.Python.valueToCode(block, 'dict_value', Blockly.Python.ORDER_ATOMIC) || "''";

        const code = `${key}: ${value}, `;
        return code;
    };

    python.pythonGenerator.forBlock['dict_to_json'] = function (block, generator) {
        const dict = Blockly.Python.valueToCode(block, 'dict', Blockly.Python.ORDER_ATOMIC) || "{}";

        const code = `json.dumps(${dict})`;
        return [code, Blockly.Python.ORDER_ATOMIC];
    };

    python.pythonGenerator.forBlock['json_to_dict'] = function (block, generator) {
        const dict = Blockly.Python.valueToCode(block, 'json', Blockly.Python.ORDER_ATOMIC) || "{}";

        const code = `json.loads(${dict})`;
        return [code, Blockly.Python.ORDER_ATOMIC];
    };
}

function defineZionGenerators() {
    python.pythonGenerator.forBlock["device_list"] = function (block) {
        var device = block.getFieldValue('device');
        var code = `"${device}"`;
        return [code, Blockly.Python.ORDER_ATOMIC];
    };

    python.pythonGenerator.forBlock["scope_list"] = function (block) {
        var scope = block.getFieldValue('scope');
        var code = `Scope("${scope}")`;
        return [code, Blockly.Python.ORDER_ATOMIC];
    };

    python.pythonGenerator.forBlock["alarm_severity_list"] = function (block) {
        var severity = block.getFieldValue('severity');
        var code = `AlarmSeverity("${severity}")`;
        return [code, Blockly.Python.ORDER_ATOMIC];
    };

    python.pythonGenerator.forBlock["alarm_search_status_list"] = function (block) {
        var search_status = block.getFieldValue('search_status');
        var code = `AlarmSearchStatus("${search_status}")`;
        return [code, Blockly.Python.ORDER_ATOMIC];
    };

    python.pythonGenerator.forBlock['device_last_telemetry'] = function (block, generator) {
        var device = generator.valueToCode(block, 'device', python.Order.ATOMIC);
        var keys = generator.valueToCode(block, 'keys', python.Order.ATOMIC);

        var code = `zion_device_last_telemetry(zion, ${device}, ${keys})`

        return [code, Blockly.Python.ORDER_ATOMIC];
    };

    python.pythonGenerator.forBlock['send_device_last_telemetry'] = function (block, generator) {
        const device = generator.valueToCode(block, 'device', python.Order.ATOMIC);
        const key = generator.valueToCode(block, 'key', python.Order.ATOMIC);
        const payload = generator.valueToCode(block, 'payload', python.Order.ATOMIC);

        const code = `zion_send_device_last_telemetry(zion, ${device}, ${key}, ${payload})`

        return [code, Blockly.Python.ORDER_ATOMIC];
    };

    python.pythonGenerator.forBlock['send_device_attr'] = function (block, generator) {
        const device = generator.valueToCode(block, 'device', python.Order.ATOMIC);
        const scope = generator.valueToCode(block, 'scope', python.Order.ATOMIC);
        const key = generator.valueToCode(block, 'key', python.Order.ATOMIC);
        const payload = generator.valueToCode(block, 'payload', python.Order.ATOMIC);

        const code = `zion_send_device_attr(zion, ${device}, ${scope}, ${key}, ${payload})`

        return [code, Blockly.Python.ORDER_ATOMIC];
    };


    python.pythonGenerator.forBlock['device_attr'] = function (block, generator) {
        var device = generator.valueToCode(block, 'device', python.Order.ATOMIC);
        var scope = generator.valueToCode(block, 'scope', python.Order.ATOMIC);
        var keys = generator.valueToCode(block, 'keys', python.Order.ATOMIC);

        var code = `zion_device_attr(zion, ${device}, ${scope}, ${keys})`

        return [code, Blockly.Python.ORDER_ATOMIC];
    };

    python.pythonGenerator.forBlock['device_alarm'] = function (block, generator) {
        var device = generator.valueToCode(block, 'device', python.Order.ATOMIC);
        var severity = generator.valueToCode(block, 'severity', python.Order.ATOMIC);
        var search_status = generator.valueToCode(block, 'search_status', python.Order.ATOMIC);

        var code = `zion_device_alarm(zion, ${device}, ${severity}, ${search_status})`

        return [code, Blockly.Python.ORDER_ATOMIC];
    };
    
    python.pythonGenerator.forBlock['send_device_alarm'] = function (block, generator) {
        var device = generator.valueToCode(block, 'device', python.Order.ATOMIC);
        var name = generator.valueToCode(block, 'name', python.Order.ATOMIC);

        var code = `zion_send_device_alarm(zion, ${device}, ${name})`

        return [code, Blockly.Python.ORDER_ATOMIC];
    };

    python.pythonGenerator.forBlock['delete_device_attr'] = function (block, generator) {
        var device = generator.valueToCode(block, 'device', python.Order.ATOMIC);
        var scope = generator.valueToCode(block, 'scope', python.Order.ATOMIC);
        var key = generator.valueToCode(block, 'key', python.Order.ATOMIC);

        var code = `zion_delete_device_attr(zion,${device},${scope},${key})`

        return [code, Blockly.Python.ORDER_ATOMIC];
    };
}

function defineRos2Generators(){
    python.pythonGenerator.forBlock['ros2_command'] = function(block, generator) {
        const command = block.getFieldValue('command');
        return `ros2_run(ros2, "${command}")\n`;
    };

    python.pythonGenerator.forBlock['ros2_subscribe'] = function(block, generator) {
        let variables = block.workspace.getAllVariables().map((v) => {
            return v.name;
        }).join(', ');

        if (variables.length > 0){
            variables = `${Blockly.Python.INDENT}global ${variables}\n`;
        }

        const value_topic = generator.valueToCode(block, 'topic', python.Order.ATOMIC);
        // const message_type = generator.valueToCode(block, 'message_type', python.Order.ATOMIC);
        const function_name = clean_topic_names(value_topic);
        const statement_function = generator.statementToCode(block, 'function');

        const code = `def ${function_name}(logging_queue: LoggingQueue):\n` + variables +  statement_function;
        return code;
    }

    python.pythonGenerator.forBlock['ros2_publish'] = function(block, generator) {
        const value_topic = generator.valueToCode(block, 'topic', python.Order.ATOMIC);
        const message_type = generator.valueToCode(block, 'message_type', python.Order.ATOMIC);

        const code = `ros2_publish(ros2, ${value_topic}, ${message_type})\n`
        return code;
    }

    python.pythonGenerator.forBlock['ros2_message_type'] = function(block) {
        const command = block.getFieldValue('message_type');
        return [command, Blockly.Python.ORDER_ATOMIC];
    };

    python.pythonGenerator.forBlock['ros2_message_String'] = function(block, generator) {
        const data = generator.valueToCode(block, 'data', python.Order.ATOMIC);
        const command = `String(data=${data})`;
        return [command, Blockly.Python.ORDER_ATOMIC];
    };

    python.pythonGenerator.forBlock['ros2_message_Bool'] = function(block, generator) {
        const data = generator.valueToCode(block, 'data', python.Order.ATOMIC);
        const command = `Bool(data=${data})`;
        return [command, Blockly.Python.ORDER_ATOMIC];
    };

    python.pythonGenerator.forBlock['ros2_message_Int64'] = function(block, generator) {
        const data = generator.valueToCode(block, 'data', python.Order.ATOMIC);
        const command = `Int64(data=${data})`;
        return [command, Blockly.Python.ORDER_ATOMIC];
    };

    python.pythonGenerator.forBlock['ros2_message_Float64'] = function(block, generator) {
        const data = generator.valueToCode(block, 'data', python.Order.ATOMIC);
        const command = `Float64(data=${data})`;
        return [command, Blockly.Python.ORDER_ATOMIC];
    };

    python.pythonGenerator.forBlock["ros2_message_Action_type"] = function (block) {
        var type = block.getFieldValue('type');
        var code = `Action.${type}`;
        return [code, Blockly.Python.ORDER_ATOMIC];
    };

    python.pythonGenerator.forBlock['ros2_message_Action'] = function(block, generator) {
        const type = generator.valueToCode(block, 'type', python.Order.ATOMIC);
        const payload = generator.valueToCode(block, 'payload', python.Order.ATOMIC) || "{}";
        const command = `Action(type=${type}, payload=${payload})`;
        return [command, Blockly.Python.ORDER_ATOMIC];
    };

    python.pythonGenerator.forBlock["ros2_message_Intent_type"] = function (block) {
        var type = block.getFieldValue('type');
        var code = `Intent.${type}`;
        return [code, Blockly.Python.ORDER_ATOMIC];
    };

    python.pythonGenerator.forBlock['ros2_message_Intent'] = function(block, generator) {
        const type = generator.valueToCode(block, 'type', python.Order.ATOMIC);
        const payload = generator.valueToCode(block, 'payload', python.Order.ATOMIC) || "{}";
        const command = `Intent(type=${type}, payload=${payload})`;
        return [command, Blockly.Python.ORDER_ATOMIC];
    };

    python.pythonGenerator.forBlock['ros2_message_Point2D'] = function(block, generator) {
        const x = generator.valueToCode(block, 'x', python.Order.ATOMIC);
        const y = generator.valueToCode(block, 'y', python.Order.ATOMIC);
        const command = `Point2D(x=${x}, y=${y})`;
        return [command, Blockly.Python.ORDER_ATOMIC];
    };

    python.pythonGenerator.forBlock['ros2_message_Marker'] = function(block, generator) {
        const id = generator.valueToCode(block, 'marker_id', python.Order.ATOMIC);
        const p1 = generator.valueToCode(block, 'p1', python.Order.ATOMIC);
        const p2 = generator.valueToCode(block, 'p2', python.Order.ATOMIC);
        const p3 = generator.valueToCode(block, 'p3', python.Order.ATOMIC);
        const p4 = generator.valueToCode(block, 'p4', python.Order.ATOMIC);
        const command = `Marker(id=${id}, p1=${p1}, p2=${p2}, p3=${p3}, p4=${p4})`;
        return [command, Blockly.Python.ORDER_ATOMIC];
    };
}

function defineMQTTGenerators(){
    python.pythonGenerator.forBlock['mqtt_subscribe'] = function(block, generator) {
        let variables = block.workspace.getAllVariables().map((v) => {
            return v.name;
        }).join(', ');

        if (variables.length > 0){
            variables = `${Blockly.Python.INDENT}global ${variables}\n`;
        }

        const value_topic = generator.valueToCode(block, 'topic', python.Order.ATOMIC);
        const function_name = clean_topic_names(value_topic);
        const statement_function = generator.statementToCode(block, 'function');

        const code = `def ${function_name}(logging_queue: LoggingQueue):\n` + variables +  statement_function;
        return code;
    }

    python.pythonGenerator.forBlock['mqtt_publish'] = function(block, generator) {
        const value_payload = generator.valueToCode(block, 'payload', python.Order.ATOMIC);
        const value_topic = generator.valueToCode(block, 'topic', python.Order.ATOMIC);

        const code = `mqtt_publish(mqtt, ${value_topic}, ${value_payload})\n`
        return code;
    }
}

function clean_topic_names(topic){
    return topic
        .replaceAll("/", "_")
        .replaceAll("\\", "_")
        .replaceAll(" ", "_")
        .replaceAll("'", "");
}
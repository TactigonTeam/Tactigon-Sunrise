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

import importlib.util
import json
import shutil
import sys
import time
from uuid import UUID
from queue import Queue

from os import path, makedirs
from typing import List, Optional, Tuple, Any

from flask import Flask

from sunrise_app.modules.shapes.models import ShapeConfig, DebugMessage, Program, ShapesPostAction

from sunrise_app.modules.zion.extension import ZionInterface
from sunrise_app.modules.ros2.extension import Ros2Interface
from sunrise_app.modules.ros2.models import RosMessage, Ros2Subscription
from sunrise_app.modules.mqtt.extension import MQTTClient, mqtt_client

from sunrise_app.extensions.base import ExtensionThread, ExtensionApp

class LoggingQueue(Queue):
    def debug(self, msg: str):
        self.put_nowait(DebugMessage.Debug(msg))

    def info(self, msg: str):
        self.put_nowait(DebugMessage.Info(msg))

    def warning(self, msg: str):
        self.put_nowait(DebugMessage.Warning(msg))

    def error(self, msg: str):
        self.put_nowait(DebugMessage.Error(msg))

    def prompt(self, msg: Any):
        self.put_nowait(DebugMessage.Prompt(msg))

class ShapeThread(ExtensionThread):
    MODULE_NAME: str = "ShapeThreadModule"
    TOUCH_DEBOUCE_TIME: float = 0.05
    TOUCH_DEBOUNCE_TIMEOUT: float = 0.2

    _logging_queue: LoggingQueue
    _zion_interface: Optional[ZionInterface] = None
    _ros2_interface: Optional[Ros2Interface] = None
    _ros2_subscription: list[Ros2Subscription] = []
    _mqtt_interface: Optional[MQTTClient] = None
    
    def __init__(
            self, 
            base_path: str, 
            app: ShapeConfig, 
            zion: Optional[ZionInterface], 
            ros2_interface: Ros2Interface | None,
            logging_queue: LoggingQueue,
        ):
        self._logging_queue = logging_queue
        self._zion_interface = zion
        self._ros2_interface = ros2_interface

        if self._ros2_interface and app.ros2_config:
            self._ros2_subscription = app.ros2_config.subscriptions
            self._ros2_interface.start(app.ros2_config, self.on_ros2_message)
        
        if app.mqtt_config:
            self._mqtt_interface = MQTTClient(app.mqtt_config, self.on_message)

        ExtensionThread.__init__(self)

        self.load_module(path.join(base_path, "programs", app.id.hex, "program.py"))

    @property
    def zion_interface(self) -> Optional[ZionInterface]:
        return self._zion_interface

    @zion_interface.setter
    def zion_interface(self, zion_interface: Optional[ZionInterface]):
        self._zion_interface = zion_interface
    
    @property
    def ros2_interface(self) -> Optional[Ros2Interface]:
        return self._ros2_interface

    @ros2_interface.setter
    def ros2_interface(self, ros2_interface: Optional[Ros2Interface]):
        self._ros2_interface = ros2_interface
    
    def on_ros2_message(self, message: RosMessage):
        if not self._ros2_interface or not self.module:
            return
        
        subscription = next((s for s in self._ros2_subscription if s.topic == message.topic), None)

        if not subscription:
            return  
                
        # Set the payload reference first
        setattr(self.module, subscription.payload_reference, message.msg.data)
        # Execute the function
        getattr(self.module, subscription.function)(self._logging_queue)
        # Clear the payload
        setattr(self.module, subscription.payload_reference, None)
    
    def on_message(self, client: mqtt_client.Client, userdata: dict, message: mqtt_client.MQTTMessage):
        if not self._mqtt_interface or not self.module:
            return
        
        subscription = next((s for s in self._mqtt_interface.config.subscriptions if s.topic == message.topic), None)

        if not subscription:
            return
        
        # Set the payload reference first
        setattr(self.module, subscription.payload_reference, json.loads(message.payload))
        # Execute the function
        getattr(self.module, subscription.function)(self._logging_queue)
        # Clear the payload
        setattr(self.module, subscription.payload_reference, None)

    def run(self):
        try:
            self.module.sunrise_app_setup(
                self.zion_interface, 
                self._ros2_interface,
                self._mqtt_interface,
                self._logging_queue
            )
        except Exception as e:
            print(e)
            self._logging_queue.error(str(e))
        
        ExtensionThread.run(self)

    def main(self):
        try:
            self.module.sunrise_app_function(
                self.zion_interface, 
                self._ros2_interface,
                self._mqtt_interface,
                self._logging_queue
            )
        except Exception as e:
            self._logging_queue.error(str(e))

    def load_module(self, source: str):
        """
        reads file source and loads it as a module

        :param source: file to load
        :param module_name: name of module to register in sys.modules
        :return: loaded module
        """
        spec = importlib.util.spec_from_file_location(self.MODULE_NAME, source)
        self.module = importlib.util.module_from_spec(spec)  # type: ignore
        sys.modules[self.MODULE_NAME] = self.module
        spec.loader.exec_module(self.module)  # type: ignore

    def stop(self):
        try:
            self.module.sunrise_app_close(
                self.zion_interface, 
                self._ros2_interface,
                self._mqtt_interface,
                self._logging_queue
            )
        except Exception as e:
            print(e)
            pass

        if self._ros2_interface:
            self._ros2_interface.stop()
            
        if self._mqtt_interface:
            self._mqtt_interface.disconnect()
            self._mqtt_interface = None

        ExtensionThread.stop(self)


class ShapesApp(ExtensionApp):
    config_file_path: str
    config: List[ShapeConfig]
    shapes_file_path: str
    current_id: Optional[UUID] = None
    logging_queue: LoggingQueue

    _zion_interface: Optional[ZionInterface] = None
    _ros2_interface: Ros2Interface | None = None

    def __init__(self, config_path: str, flask_app: Optional[Flask] = None):
        self.config_file_path = path.join(config_path, "config.json")
        self.shapes_file_path = config_path
        self.logging_queue = LoggingQueue()

        with open(self.config_file_path) as cfg:
            self.config = [ShapeConfig.FromJSON(c) for c in json.load(cfg)]

        ExtensionApp.__init__(self, flask_app)

    @property
    def zion_interface(self) -> Optional[ZionInterface]:
        return self._zion_interface

    @zion_interface.setter
    def zion_interface(self, zion_interface: Optional[ZionInterface]):
        self._zion_interface = zion_interface

    @property
    def ros2_interface(self) -> Optional[Ros2Interface]:
        return self._ros2_interface

    @ros2_interface.setter
    def ros2_interface(self, ros2_interface: Optional[Ros2Interface]):
        self._ros2_interface = ros2_interface


    def get_log(self) -> Optional[DebugMessage]:
        try:
            return self.logging_queue.get_nowait()
        except:
            return None

    def get_state(self, program_id: UUID) -> Optional[dict]:
        try:
            folder_path = path.join(self.shapes_file_path, "programs", program_id.hex)
            state_file_path = path.join(folder_path, "state.json")

            with open(state_file_path) as state_json_file:
                return json.load(state_json_file)

        except FileNotFoundError:
            print(f"Error: The file {self.config_file_path} does not exist.")

        except json.JSONDecodeError:
            print("Error: The file is not a valid JSON document.")

        return None

    def add(self, config: ShapeConfig, program: Optional[Program] = None) -> bool:
        self.save_config(config)

        if not program:
            program = self.get_shape()

        return self.__create_or_update_files(config.id, program)
    
    def save_config(self, config: Optional[ShapeConfig] = None):
        if config:
            found = False

            for i, cfg in enumerate(self.config):
                if cfg.id == config.id:
                    self.config[i] = config
                    found = True
                    break

            if not found:
                self.config.append(config)

        with open(self.config_file_path, "w") as config_file:
            json.dump([cfg.toJSON() for cfg in self.config], config_file, indent=2)

    def update(self, config: ShapeConfig, program: Program) -> bool:
        self.save_config(config)
        return self.__create_or_update_files(config.id, program)

    def remove(self, program_id: UUID):
        filtered_programs = [c for c in self.config if c.id != program_id]

        self.config = filtered_programs

        with open(self.config_file_path, "w") as config_file:
            json.dump([cfg.toJSON() for cfg in self.config], config_file, indent=2)

        folder_path = path.join(self.shapes_file_path, "programs", program_id.hex)
        shutil.rmtree(folder_path)

    def find_shape_by_id(self, config_id: UUID) -> Optional[ShapeConfig]:
        return next(filter(lambda x: x.id == config_id, self.config), None)

    def find_shape_by_name(self, name: str) -> Optional[ShapeConfig]:
        return next((c for c in self.config if c.name.strip().lower() == name.strip().lower()), None)

    def find_shape_by_name_and_not_id(self, name: str, config_id: UUID) -> Optional[ShapeConfig]:
        return next((c for c in self.config if c.id != config_id and c.name.strip().lower() == name.strip().lower()), None)

    def get_blocks_congfig(self) -> dict:

        data = {}

        return data
    
    def get_shape(self, uuid: Optional[UUID] = None) -> Program:
        code = None
        program_file = None

        if uuid:
            state_file = path.join(self.shapes_file_path, "programs", uuid.hex, "state.json")
            program_file = path.join(self.shapes_file_path, "programs", uuid.hex, "program.py")
        else:
            state_file = path.join(self.shapes_file_path, "init_state.json")

        with open(state_file) as state_json_file:
            state = json.load(state_json_file)

        if program_file:
            try:
                with open(program_file) as program_python_file:
                    code = program_python_file.read()
            except:
                pass

        return Program(state, code)

    def start(self, config_id: UUID) -> Optional[Tuple[bool, str]]:
        if self.is_running:
            self.stop()

        for _config in self.config:
            if _config.id == config_id:

                current_program = self.get_shape(_config.id)

                if current_program.code is None:
                    return (False, "Code not found")

                self.current_id = _config.id
                try:
                    self.thread = ShapeThread(
                        self.shapes_file_path, 
                        _config,
                        self.zion_interface, 
                        self.ros2_interface,
                        self.logging_queue
                    ) 
                    self.thread.start()
                except Exception as e:
                    print(e)
                    self.current_id = None
                    if self.thread:
                        try:
                            self.thread.stop()
                        except:
                            pass
                    self.thread = None
                    return (False, str(e))
                return (True, "")

        return None
    
    def stop(self):
        ExtensionApp.stop(self)
        while True:
            if not self.get_log():
                break

    def __create_or_update_files(self, config_id: UUID, program: Program) -> bool:
        folder_path = path.join(self.shapes_file_path, "programs", config_id.hex)
        python_file_path = path.join(folder_path, 'program.py')
        state_file_path = path.join(folder_path, 'state.json')

        if not path.exists(folder_path):
            makedirs(folder_path)

        if program.code:
            with open(python_file_path, "w", newline="", encoding="utf-8") as python_file:
                python_file.write(program.code)

        with open(state_file_path, "w") as state_json_file:
            json.dump(program.state, state_json_file, indent=2)
        

        return True
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

import rclpy
import os
import json
import subprocess
import signal
from rclpy.node import Node, QoSProfile
from std_msgs.msg import String
from threading import Thread, Event as ThreadEvent
from multiprocessing import Process, Queue, Event, Pipe
from queue import Queue, Empty
from functools import wraps
from flask import Flask
from werkzeug.datastructures import FileStorage

from typing import Callable, Optional, Any

from sunrise_app.modules.ros2.models import Ros2Config, Ros2Command, Ros2ShapeConfig, RosMessage, NodeAction, NodeActions, RosMessageTypes, get_message_name

class ShapeNode(Node):
    TICK: float = 0.02

    def __init__(self):
        Node.__init__(self, "sunrise_app")

    def add_publisher(self, topic: str, message_type: RosMessageTypes, qos_profile: QoSProfile | int):
        publisher = self.create_publisher(message_type, topic, qos_profile)

    def add_subscription(self, topic: str, fn: Callable[[RosMessage], None], message_type: Any, qos_profile: QoSProfile | int):
        self.create_subscription(
            message_type, 
            topic, 
            self._callback(topic, fn), 
            qos_profile
        )

    def publish(self, topic: str, msg: RosMessageTypes):
        publisher = next((p for p in self.publishers if p.topic == topic), None)

        self.get_logger().info(f"Pubblishin {msg} on {topic}")
        if publisher:
            publisher.publish(msg)

    def unsubscribe(self, topic: str):
        subscription = next((s for s in self.subscriptions if s.topic == topic), None)

        if subscription:
            self.destroy_subscription(subscription)

    def _callback(self, topic: str, fn: Callable[[RosMessage], None]):
        @wraps(fn)
        def wrapper(msg):
            result = fn(RosMessage(topic, msg))
            return result
        return wrapper

class Ros2Process(Process):
    _thread: None | Thread = None
    _thread_stop_event: ThreadEvent

    def __init__(self, config: Ros2ShapeConfig, fn: Callable[[RosMessage], None] | None = None):
        Process.__init__(self, daemon=True)
        self._config = config
        self._callback = fn
        self._stop_event = Event()
        self._in, self._out = Pipe()

    def wrap_callback(self, fn: Callable[[RosMessage], None]):
        while not self._stop_event.is_set():
            msg = self.get_msg()
            if msg:
                fn(msg)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *attr):
        self.stop()
        
    def start(self):
        for p in self._config.publishers:
            self.add_publisher(
                p.topic,
                p.message_type,
                p.qos_profile
            )

        for s in self._config.subscriptions:
            self.add_subscription(
                s.topic,
                s.message_type,
                s.qos_profile
            )

        if self._callback:
            self._thread = Thread(target=self.wrap_callback, args=(self._callback, ), daemon=True)
            self._thread.start()

        Process.start(self)

    def stop(self):
        self._stop_event.set()
        self.join(10)
          
        if self._thread:
            self._stop_event.set()
            self._thread.join()

        self._thread = None

    def run(self):
        rclpy.init()
        try:
            node = ShapeNode()

            while rclpy.ok() and not self._stop_event.is_set():
                rclpy.spin_once(node, timeout_sec=0)
                if self._in.poll():
                    node_action: NodeAction = self._in.recv()
                    action = node_action.action
                    payload = node_action.payload

                    if action == NodeActions.ADD_PUBLISHER:
                        node.add_publisher(
                            payload.get("topic", ""), 
                            payload.get("message_type", String),
                            payload.get("qos_profile", 10)
                        )
                    elif action == NodeActions.ADD_SUBSCRIPTION:
                        node.add_subscription(
                            payload.get("topic", ""), 
                            self._in.send,
                            payload.get("message_type", String),
                            payload.get("qos_profile", 10)
                        )
                    elif action == NodeActions.PUBLISH:
                        node.publish(
                            payload.get("topic", ""), 
                            payload.get("msg", String(data="Error publishing message"))
                        )
                    elif action == NodeActions.UNSUBSCRIBE:
                        node.unsubscribe(payload.get("topic", ""))

                # time.sleep(node.TICK)

            node.destroy_node()
        except Exception as e:
            print(e)

        finally:
            rclpy.shutdown()

    def _send_command(self, cmd: NodeAction):
        self._out.send(cmd)

    def get_msg(self) -> RosMessage | None:
        if self._out.poll():
            return self._out.recv()
        
        return None

    def add_publisher(self, topic: str, message_type: RosMessageTypes, qos_profile: QoSProfile | int = 10):
        self._send_command(
            NodeAction.AddPubblisher(
                dict(topic=topic, message_type=message_type, qos_profile=qos_profile)
            )
        )

    def add_subscription(self, topic: str, message_type: Any, qos_profile: QoSProfile | int = 10):
        self._send_command(
            NodeAction.AddSubscription(
                dict(topic=topic, message_type=message_type, qos_profile=qos_profile)
            )
        )

    def unsubscribe(self, topic: str):
        self._send_command(
            NodeAction.Unsubscribe(
                dict(topic=topic)
            )
        )

    def publish(self, topic: str, msg: RosMessageTypes) -> bool:
        self._send_command(
            NodeAction.Publish(
                dict(topic=topic, msg=msg)
            )
        )
        return True

class Ros2Interface:
    _process: Ros2Process | None
    _running_commands: list[subprocess.Popen]
    ros2_path: str
    config: Ros2Config

    def __init__(self, ros2_path: str, app: Flask | None = None):
        self.ros2_path = ros2_path

        self.load_config()

        self._process = None
        self._running_commands = []

        if app:
            self.init_app(app)

    def init_app(self, app: Flask):
        app.extensions[Ros2Interface.__name__] = self

    def get_blocks(self):
        return {
            "default_types": [(n, n) for n in get_message_name()],
            "commands": [(c.name, c.identifier) for c in self.config.ros2_commands] if self.config.ros2_commands else [("", "")],
            "action_types": [("GESTURE", "GESTURE"), ("VOICE_COMMAND", "VOICE_COMMAND"), ("TOUCH", "TOUCH"), ("CAMERA_POINT", "CAMERA_POINT"), ("MARKER", "MARKER")],
            "intent_types": [("TEACH", "TEACH"), ("REPEAT", "REPEAT")],
        }
    
    @property
    def is_running(self) -> bool:
        return self._process.is_alive() if self._process else False
    
    @property
    def config_file(self) -> str:
        return os.path.join(self.ros2_path, "config.json")
    
    @property
    def nodes_config_folder(self) -> str:
        return os.path.join(self.ros2_path, "parameters")
    
    def load_config(self):
        if os.path.exists(self.ros2_path) and os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                config_data = json.load(f)
                self.config = Ros2Config.FromJSON(config_data)
        else:
            self.config = Ros2Config.Default()
            self.save_config()

    def save_config(self):
        if not os.path.exists(self.ros2_path):
            os.makedirs(self.ros2_path)

        with open(self.config_file, "w") as f:
            json.dump(self.config.toJSON(), f, indent=2)

        self.load_config()

    def reset_config(self):
        self.stop()
        
        if os.path.exists(self.ros2_path) and os.path.exists(self.config_file):
            os.remove(self.config_file)

        self.load_config()

    def get_package_command(self, package_name: str, node_name: str) -> Ros2Command | None:
        return next(
            (c for c in self.config.ros2_commands 
             if c.package_name == package_name and c.node_name == node_name), None)

    def add(self, package_name: str, node_name: str, param_file: FileStorage) -> bool:
        if not param_file.filename:
            return False
        
        if not os.path.exists(self.nodes_config_folder):
            os.makedirs(self.nodes_config_folder)
        
        filepath = os.path.join(self.nodes_config_folder, param_file.filename)
        param_file.save(filepath)

        self.config.ros2_commands.append(
            Ros2Command(
                package_name,
                node_name,
                param_file.filename
            )
        )

        return True
    
    def remove(self, package_name: str, node_name: str) -> bool:
        c = self.get_package_command(package_name, node_name)

        if c:
            filepath = os.path.join(self.nodes_config_folder, c.parameter_file)
            os.remove(filepath)
            self.config.ros2_commands.remove(c)

        return True

    def start(self, config: Ros2ShapeConfig, fn: Callable[[RosMessage], None] | None = None):
        if self._process:
            self.stop()

        self._process = Ros2Process(config, fn)
        self._process.start()
    
    def stop(self):
        if self._process:
            self._process.stop()
            
        for p in self._running_commands:
            if p and p.poll() is None:
                os.killpg(os.getpgid(p.pid), signal.SIGTERM)
                p.wait(timeout=5)

        self._process = None
        self._running_commands.clear()

    def run(self, command: str):
        c = next((c for c in self.config.ros2_commands if c.identifier == command), None)
        if c:
            cmd = c.get_command().split(" ")
            self._running_commands.append(
                subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    preexec_fn=os.setsid
                )
            )

    def publish(self, topic: str, msg: RosMessageTypes) -> bool:
        if self._process:
            return self._process.publish(
                topic,
                msg,        
            )
        
        return False
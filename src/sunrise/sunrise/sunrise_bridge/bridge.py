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

import json
from os import path
from rclpy.node import Node

from sunrise_msgs.msg import Action, Intent

from sunrise.sunrise_bridge.models import SunriseBridgeConfig, MappingType, GestureMapping, TouchMapping

from tactigon_gear import TSkin, Gesture, Touch

class SunriseBridge(Node):
    tskin_connection: bool

    def __init__(self, config_path: str):
        Node.__init__(self, SunriseBridge.__name__)
        self.get_logger().info("Creating SunriseBridge node")

        self.config_path = config_path
        self.config = self.load_config(config_path)

        self.get_logger().debug(f"Creating Action publisher on {self.config.action_topic}")
        self.action_publisher = self.create_publisher(Action, self.config.action_topic, 10)

        self.get_logger().debug(f"Creating Intent publisher on {self.config.action_topic}")
        self.intent_publisher = self.create_publisher(Intent, self.config.intent_topic, 10)

        self.get_logger().info("Creating Tactigon Skin instance and timer")
        self.tskin_connection = False
        self.tskin = TSkin(self.config.tskin_config)
        self.get_logger().debug("Tactigon Skin created!")
        self.tskin.start()
        self.get_logger().debug("Tactigon Skin started")
        self.tskin_job = self.create_timer(0.02, self._do_tskin_job)
        self.get_logger().info("Created!")

    def load_config(self, config_path: str) -> SunriseBridgeConfig:
        with open(config_path) as cf:
            return SunriseBridgeConfig.FromJSON(json.load(cf))

    def _get_mapping_from_gesture(self, gesture: Gesture) -> GestureMapping | None:
        return next((gm for gm in self.config.gestures if gm.gesture == gesture.gesture), None)
    
    def _get_mapping_from_touch(self, touch: Touch) -> TouchMapping | None:
        return next((tm for tm in self.config.touchs if tm.touch == touch.one_finger.name or tm.touch == touch.two_finger.name), None)
    
    def _send_action(self, payload: dict):
        a = Action()
        a.type = Action.GESTURE
        a.payload = json.dumps(payload)

        self.get_logger().info(f"Sending Action {a}")
        self.action_publisher.publish(a)

    def _send_teach_intent(self, payload: dict):
        i = Intent()
        i.type = Intent.TEACH
        i.payload = json.dumps(payload)
        self.get_logger().info(f"Sending Intent {i}")
        self.intent_publisher.publish(i)

    def _send_repeat_intent(self, payload: dict):
        i = Intent()
        i.type = Intent.REPEAT
        i.payload = json.dumps(payload)
        self.get_logger().info(f"Sending Intent {i}")
        self.intent_publisher.publish(i)

    def _send_payload_by_mapping(self, mapping: GestureMapping | TouchMapping, payload: dict):
        if mapping.mapping == MappingType.ACTION:
            self._send_action(payload)
        elif mapping.mapping == MappingType.LEARN_INTENT:
            self._send_teach_intent(payload)
        elif mapping.mapping == MappingType.REPEAT_INTENT:
            self._send_repeat_intent(payload)

    def _do_tskin_job(self):
        if self.tskin_connection != self.tskin.connected:
            if self.tskin.connected:
                self.get_logger().info(f"TSkin connected -> {self.tskin.config.address} on hand {self.tskin.config.hand}")
            else:
                self.get_logger().warn(f"TSkin disconnected -> {self.tskin.config.address} on hand {self.tskin.config.hand}")

            self.tskin_connection = self.tskin.connected

        if not self.tskin.connected:
            return
        
        self.get_logger().debug(f"TSkin connected -> {self.tskin.config.address} on hand {self.tskin.config.hand}")
        
        gesture = self.tskin.gesture
        touch = self.tskin.touch

        if gesture:
            gesture_mapping = self._get_mapping_from_gesture(gesture)
            payload = gesture.toJSON()
            
            if gesture_mapping:
                self._send_payload_by_mapping(gesture_mapping, payload)
            else:
                self.get_logger().warn(f"No mapping for gesture {payload}")

        if touch:
            touch_mapping = self._get_mapping_from_touch(touch)
            payload = touch.toJSON()
            
            if touch_mapping:
                self._send_payload_by_mapping(touch_mapping, payload)
            else:
                self.get_logger().warn(f"No mapping for touch {payload}")


    def destroy_node(self):
        self.tskin.join(5)
        Node.destroy_node(self)
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

import time
import json
from queue import Queue
from typing import Optional, Callable

import paho.mqtt.client as mqtt_client

from .models import MQTTConfig

class MQTTClient:
    config: MQTTConfig
    userdata: dict

    client: Optional[mqtt_client.Client] = None

    _can_reconnect: bool

    def __init__(self, config: MQTTConfig, on_message: Optional[Callable[[mqtt_client.Client, dict, mqtt_client.MQTTMessage], None]] = None):
        self.config = config
        self._can_reconnect = True
        
        self.userdata = {}
        self.client = mqtt_client.Client(
            client_id=self.config.node_name,
            callback_api_version=self.config.callback_api_version,
            protocol=self.config.protocol_version,
            userdata=self.userdata,
        )
        
        self.client.connect(self.config.broker_url, self.config.broker_port)
        self.client.loop_start()
        self.client.on_disconnect=self.on_disconnect
        self.client.on_connect=self.add_subscriptions()
        if on_message:
            self.client.on_message = on_message
        else:
            self.client.on_message=self.on_message

    @property
    def connected(self):
        return self.client.is_connected() if self.client else False

    def add_subscriptions(self):
        if not self.client:
            return
        
        for s in self.config.subscriptions:
            self.client.subscribe(
            topic=s.topic,
            qos=s.qos
        )

    def on_disconnect(self, client: mqtt_client.Client, *args):
        if not self._can_reconnect:
            return
        
        if not self.client:
            return
                
        reconnect_count = reconnect_delay = 0
        # while reconnect_count < self.config.max_reconnect_count:
        while True:
            time.sleep(reconnect_delay)

            try:
                self.client.reconnect()
                return
            except Exception as err:
                pass

            reconnect_delay = reconnect_count * self.config.reconnect_rate
            reconnect_count += 1

        self.client = None

    def on_message(self, client: mqtt_client.Client, userdata: dict, message: mqtt_client.MQTTMessage):
        print(message.topic, message.payload)

    def subscribe(self, topic: str, qos: int = 0, timeout: float = 5):
        if not self.client:
            return
        
        _t = 0
        while not self.client.is_connected():
            time.sleep(0.05)
            _t += 0.05
            if _t > timeout:
                return False
        
        self.client.subscribe(
            topic=topic,
            qos=qos
        )

    def publish(self, topic: str, payload: dict, qos: int = 0, timeout: float = 5) -> bool:
        if not self.client:
            return False
        
        _t = 0
        while not self.client.is_connected():
            time.sleep(0.05)
            _t += 0.05
            if _t > timeout:
                return False
        
        try:
            self.client.publish(
                topic=topic,
                payload=json.dumps(payload),
                qos=qos,
            )
        except Exception as e:
            return False

        return True
    
    def disconnect(self):
        self._can_reconnect = False
        if self.client:
            self.client.disconnect()
        
        self.client = None
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
import wave
import time

from pyaudio import PyAudio, paContinue
from os import path
from rclpy.node import Node

from sunrise_msgs.msg import Action, Intent, Gesture as Gesture_msg, Transcription as Transcription_msg

from sunrise.sunrise_bridge.models import SunriseBridgeConfig, MappingType, GestureMapping, TouchMapping, TranscriptionMapping

from tactigon_gear.tskin_socket import TSkinSocket, TSkinConfig, SocketConfig
from tactigon_gear.models.tskin import Touch, Gesture
from tactigon_gear.models.audio import Transcription

class SunriseBridge(Node):
    tskin_connection: bool

    def __init__(self, config_path: str):
        Node.__init__(self, SunriseBridge.__name__)
        self.get_logger().info("Creating SunriseBridge node")

        self.config_path = config_path
        self.config = self.load_config(config_path)

        self.pa = PyAudio()

        self.gesture_publisher = self.create_publisher(Gesture_msg, "/human/body/1/gesture", 10)
        self.live_speech_publisher = self.create_publisher(Transcription_msg, "/human/voices/1/livespeech", 10)

        self.get_logger().debug(f"Creating Action publisher on {self.config.action_topic}")
        self.action_publisher = self.create_publisher(Action, self.config.action_topic, 10)

        self.get_logger().debug(f"Creating Intent publisher on {self.config.action_topic}")
        self.intent_publisher = self.create_publisher(Intent, self.config.intent_topic, 10)

        self.get_logger().info("Creating Tactigon Skin instance and timer")
        self.tskin_connection = False
        self.tskin = TSkinSocket(self.config.tskin_config, self.config.socket_config)
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
    
    def _get_mapping_from_transcription(self, transcription: Transcription) -> TranscriptionMapping | None:
        self.get_logger().info(f"TST: {'_'.join((hw.word for hw in transcription.path))}")
        return next((tm for tm in self.config.transcriptions if tm.command == "_".join((hw.word for hw in transcription.path))), None)
        
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

    def _send_payload_by_mapping(self, mapping: GestureMapping | TouchMapping | TranscriptionMapping, payload: dict):
        payload["mapping"] = mapping.mapping.name

        if mapping.mapping == MappingType.ACTION:
            self._send_action(payload)
        elif mapping.mapping in [MappingType.TEACH_SKILL, MappingType.TEACH_TASK]:
            self._send_teach_intent(payload)
        elif mapping.mapping in [MappingType.REPEAT_SKILL, MappingType.REPEAT_TASK]:
            self._send_repeat_intent(payload)
        elif mapping.mapping == MappingType.SPEECH:
            self.tskin.listen(self.config.speech)

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
        text_so_far = self.tskin.text_so_far
        transcription = self.tskin.transcription

        if gesture:
            g = Gesture_msg()
            g.type = 0
            g.payload = gesture.gesture
            self.gesture_publisher.publish(g)

            gesture_mapping = self._get_mapping_from_gesture(gesture)
            payload = gesture.toJSON()
            
            if gesture_mapping:
                self._send_payload_by_mapping(gesture_mapping, payload)
            else:
                self.get_logger().warn(f"No mapping for gesture {payload}")

        if touch:
            g = Gesture_msg()
            g.type = 1
            g.payload = touch.one_finger or touch.two_finger
            self.gesture_publisher.publish(g)

            touch_mapping = self._get_mapping_from_touch(touch)
            payload = touch.toJSON()
            
            if touch_mapping:
                self._send_payload_by_mapping(touch_mapping, payload)
            else:
                self.get_logger().warn(f"No mapping for touch {payload}")

        if text_so_far:
            t = Transcription_msg()
            t.text_so_far = text_so_far
            self.live_speech_publisher.publish(t)

            self.get_logger().info(f"Text so far: {text_so_far}")

        if transcription:
            t = Transcription_msg()
            t.transcription = transcription.text
            self.live_speech_publisher.publish(t)

            self.get_logger().info(f"Got transcription {transcription}")
            transcription_mapping = self._get_mapping_from_transcription(transcription)
            payload = transcription.toJSON()
            self.get_logger().info(f"Got transcription mapping {transcription_mapping}")

            if transcription_mapping:
                self.play("./start_job_confirmation.wav")
                self._send_payload_by_mapping(transcription_mapping, payload)
            
    def play(self, filename: str):
        with wave.open(filename, "rb") as f:
            def callback(in_data, frame_count, time_info, status):
                data = f.readframes(frame_count)
                return (data, paContinue)

            audio_stream = self.pa.open(
                format=self.pa.get_format_from_width(f.getsampwidth()),
                channels=f.getnchannels(),
                rate=f.getframerate(),
                output=True,
                stream_callback=callback
            )

            while audio_stream.is_active():
                time.sleep(0.5)

            audio_stream.close()

    def destroy_node(self):
        self.tskin.join(5)
        Node.destroy_node(self)
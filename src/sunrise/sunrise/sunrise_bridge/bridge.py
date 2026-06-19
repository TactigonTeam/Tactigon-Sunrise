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
from rclpy.node import Node
from rclpy.qos import QoSPresetProfiles, QoSProfile, QoSReliabilityPolicy, QoSDurabilityPolicy, QoSHistoryPolicy

from std_msgs.msg import String
from sunrise_msgs.msg import Action, Intent, Gesture as Gesture_msg, Transcription as Transcription_msg

# QoS for high-frequency sensor data: must match SENSOR_DATA QoS used by sunrise_tactigon publishers
SENSOR_QOS = QoSPresetProfiles.SENSOR_DATA.value
# QoS for reliable command/event messages: guarantee delivery, no durability persistence needed
RELIABLE_QOS = QoSProfile(
    reliability=QoSReliabilityPolicy.RELIABLE,
    durability=QoSDurabilityPolicy.VOLATILE,
    history=QoSHistoryPolicy.KEEP_LAST,
    depth=10
)

from sunrise.sunrise_bridge.models import SunriseBridgeConfig, MappingType, GestureMapping, TouchMapping, TranscriptionMapping

from tactigon_gear.models.tskin import Touch, Gesture, OneFingerGesture, TwoFingerGesture
from tactigon_gear.models.audio import Transcription, HotWord

class SunriseBridge(Node):
    tskin_connection: bool

    def __init__(self, config_path: str):
        Node.__init__(self, SunriseBridge.__name__)
        self.get_logger().info("Creating SunriseBridge node")

        self.config_path = config_path
        self.config = self.load_config(config_path)

        self.pa = PyAudio()

        self.gesture_subscription = self.create_subscription(Gesture_msg, "/human/body/person1/gesture", self._on_gesture, SENSOR_QOS)
        self.live_speech_subscription = self.create_subscription(Transcription_msg, "/human/voices/person1/livespeech", self._on_transcription, SENSOR_QOS)
        self.speech_request_publisher = self.create_publisher(String, "/human/voice/person1/stream", RELIABLE_QOS)

        self.get_logger().debug(f"Creating Action publisher on {self.config.action_topic}")
        self.action_publisher = self.create_publisher(Action, self.config.action_topic, RELIABLE_QOS)

        self.get_logger().debug(f"Creating Intent publisher on {self.config.action_topic}")
        self.intent_publisher = self.create_publisher(Intent, self.config.intent_topic, RELIABLE_QOS)

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
            self.speech_request_publisher.publish(String())

    def _on_gesture(self, message: Gesture_msg):
        if message.type == 1: # touch
            touch = None
            for t in OneFingerGesture:
                if t.name == message.payload:
                    touch = Touch(
                        t,
                        TwoFingerGesture.NONE,
                        0,
                        0,
                    )

            for t in TwoFingerGesture:
                if t.name == message.payload:
                    touch = Touch(
                        OneFingerGesture.NONE,
                        t,
                        0,
                        0,
                    )
                    
            if touch:
                touch_mapping = self._get_mapping_from_touch(touch)
                payload = touch.toJSON()
                
                if touch_mapping:
                    self._send_payload_by_mapping(touch_mapping, payload)
                else:
                    self.get_logger().warn(f"No mapping for touch {payload}")
        else:
            gesture = Gesture(message.payload, 0, 0, 0)

            gesture_mapping = self._get_mapping_from_gesture(gesture)
            payload = gesture.toJSON()
            
            if gesture_mapping:
                self._send_payload_by_mapping(gesture_mapping, payload)
            else:
                self.get_logger().warn(f"No mapping for gesture {payload}")

    def _on_transcription(self, message: Transcription_msg):
        
        self.get_logger().info(f"Text so far: {message.text_so_far}")

        if message.transcription:
            transcription = Transcription(
                message.transcription,
                [HotWord(word) for word in message.path],
                message.time,
                message.timeout
            )

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
        Node.destroy_node(self)
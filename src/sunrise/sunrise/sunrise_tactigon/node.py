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
from sunrise_msgs.msg import Gesture as Gesture_msg, Transcription as Transcription_msg

# QoS for high-frequency sensor data: drop stale readings, no need for delivery guarantee
SENSOR_QOS = QoSPresetProfiles.SENSOR_DATA.value
# QoS for reliable control messages: guarantee delivery
RELIABLE_QOS = QoSProfile(
    reliability=QoSReliabilityPolicy.RELIABLE,
    durability=QoSDurabilityPolicy.VOLATILE,
    history=QoSHistoryPolicy.KEEP_LAST,
    depth=1
)

from sunrise.sunrise_tactigon.models import TactigonConfig
from tactigon_gear.tskin_socket import TSkinSocket

class TactigonNode(Node):
    tskin_connection: bool

    def __init__(self, config_path: str):
        Node.__init__(self, TactigonNode.__name__)
        self.get_logger().info("Creating SunriseBridge node")

        self.config_path = config_path
        self.config = self.load_config(config_path)

        self.pa = PyAudio()

        self.gesture_publisher = self.create_publisher(Gesture_msg, "/human/body/person1/gesture", SENSOR_QOS)
        self.live_speech_publisher = self.create_publisher(Transcription_msg, "/human/voices/person1/livespeech", SENSOR_QOS)
        self.speech_command_subscriber = self.create_subscription(String, "/human/voice/person1/stream", self._on_stream_request, RELIABLE_QOS)

        self.get_logger().info("Creating Tactigon Skin instance and timer")
        self.tskin_connection = False
        self.tskin = TSkinSocket(self.config.tskin_config, self.config.socket_config)
        self.get_logger().debug("Tactigon Skin created!")
        self.tskin.start()
        self.get_logger().debug("Tactigon Skin started")
        self.tskin_job = self.create_timer(0.02, self._do_tskin_job)
        self.get_logger().info("Created!")

    def load_config(self, config_path: str) -> TactigonConfig:
        with open(config_path) as cf:
            return TactigonConfig.FromJSON(json.load(cf))
        
    def _on_stream_request(self, message: String):
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

        if touch:
            g = Gesture_msg()
            g.type = 1
            g.payload = touch.one_finger or touch.two_finger
            self.gesture_publisher.publish(g)

        if text_so_far:
            t = Transcription_msg()
            t.text_so_far = text_so_far
            self.live_speech_publisher.publish(t)

            self.get_logger().info(f"Text so far: {text_so_far}")

        if transcription:
            t = Transcription_msg()
            t.transcription = transcription.text
            t.text_so_far = text_so_far
            t.path = [hw.word for hw in transcription.path]
            t.time = transcription.time
            t.timeout = transcription.timeout
            self.live_speech_publisher.publish(t)
            
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
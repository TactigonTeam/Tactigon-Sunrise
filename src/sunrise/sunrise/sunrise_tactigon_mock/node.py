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

from rclpy.node import Node
from rclpy.qos import QoSPresetProfiles

from sunrise_msgs.msg import Gesture as Gesture_msg, Transcription as Transcription_msg

# QoS for high-frequency sensor data: drop stale readings, no need for delivery guarantee
SENSOR_QOS = QoSPresetProfiles.SENSOR_DATA.value

class TactigonMock(Node):
    def __init__(self):
        Node.__init__(self, TactigonMock.__name__)
        self.gesture_pubblisher = self.create_publisher(Gesture_msg, "/human/body/person1/gesture", SENSOR_QOS)
        self.live_speech_publisher = self.create_publisher(Transcription_msg, "/human/voices/person1/livespeech", SENSOR_QOS)

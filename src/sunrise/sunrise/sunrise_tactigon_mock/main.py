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

import sys
import json

import rclpy

from PyQt5.QtWidgets import (
    QApplication, QWidget, QMainWindow, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QGroupBox, QCheckBox, QDoubleSpinBox
)
from PyQt5.QtCore import QTimer

from sunrise.sunrise_tactigon_mock.node import TactigonMock
from sunrise_msgs.msg import Gesture as Gesture_msg, Transcription as Transcription_msg


class TactigonMockWindow(QMainWindow):
    def __init__(self, node: TactigonMock, parent=None):
        QMainWindow.__init__(self, parent)
        self.setWindowTitle("Tactigon Mock")
        self.resize(480, 360)

        self._node = node

        container = QWidget(self)
        main_layout = QVBoxLayout()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # --- Gesture group ---
        gesture_group = QGroupBox("Gesture")
        gesture_layout = QVBoxLayout()
        gesture_group.setLayout(gesture_layout)

        self._gesture_payload = QLineEdit()
        self._gesture_payload.setPlaceholderText("Gesture/Touch (string)")
        gesture_layout.addWidget(self._gesture_payload)

        gesture_btn_layout = QHBoxLayout()

        hand_btn = QPushButton("HAND")
        hand_btn.clicked.connect(lambda: self._publish_gesture(Gesture_msg.HAND))
        gesture_btn_layout.addWidget(hand_btn)

        touch_btn = QPushButton("TOUCH")
        touch_btn.clicked.connect(lambda: self._publish_gesture(Gesture_msg.TOUCH))
        gesture_btn_layout.addWidget(touch_btn)

        gesture_layout.addLayout(gesture_btn_layout)
        main_layout.addWidget(gesture_group)

        # --- Transcription group ---
        transcription_group = QGroupBox("Transcription")
        transcription_layout = QVBoxLayout()
        transcription_group.setLayout(transcription_layout)

        self._transcription_text = QLineEdit()
        self._transcription_text.setPlaceholderText("transcription")
        transcription_layout.addWidget(QLabel("transcription:"))
        transcription_layout.addWidget(self._transcription_text)

        self._transcription_text_so_far = QLineEdit()
        self._transcription_text_so_far.setPlaceholderText("text_so_far (optional)")
        transcription_layout.addWidget(QLabel("text_so_far:"))
        transcription_layout.addWidget(self._transcription_text_so_far)

        self._transcription_path = QLineEdit()
        self._transcription_path.setPlaceholderText("Comma-separated strings")
        transcription_layout.addWidget(QLabel("path:"))
        transcription_layout.addWidget(self._transcription_path)

        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("time:"))
        self._transcription_time = QDoubleSpinBox()
        self._transcription_time.setRange(0.0, 1e9)
        self._transcription_time.setDecimals(3)
        self._transcription_time.setSingleStep(0.1)
        time_layout.addWidget(self._transcription_time)
        transcription_layout.addLayout(time_layout)

        self._transcription_timeout = QCheckBox("timeout")
        transcription_layout.addWidget(self._transcription_timeout)

        speech_btn = QPushButton("Send Transcription")
        speech_btn.clicked.connect(self._publish_transcription)
        transcription_layout.addWidget(speech_btn)

        main_layout.addWidget(transcription_group)

        # --- Status bar ---
        self._status = QLabel("Ready")
        main_layout.addWidget(self._status)

    def _publish_gesture(self, gesture_type: int):
        msg = Gesture_msg()
        msg.type = gesture_type
        msg.payload = self._gesture_payload.text().strip()
        self._node.gesture_pubblisher.publish(msg)
        type_name = "HAND" if gesture_type == Gesture_msg.HAND else "TOUCH"
        self._node.get_logger().info(f"Published Gesture {type_name}: {msg.payload!r}")
        self._status.setText(f"Gesture {type_name} sent")

    def _publish_transcription(self):
        msg = Transcription_msg()
        msg.transcription = self._transcription_text.text().strip()
        msg.text_so_far = self._transcription_text_so_far.text().strip()
        path_raw = self._transcription_path.text().strip()
        msg.path = [p.strip() for p in path_raw.split(",") if p.strip()] if path_raw else []
        msg.time = self._transcription_time.value()
        msg.timeout = self._transcription_timeout.isChecked()
        self._node.live_speech_publisher.publish(msg)
        self._node.get_logger().info(f"Published Transcription: {msg.transcription!r}")
        self._status.setText(f"Transcription sent: {msg.transcription!r}")


class TactigonMockApp(QApplication):
    def __init__(self, args=[]):
        QApplication.__init__(self, args)

        rclpy.init()
        self._node = TactigonMock()

        self._window = TactigonMockWindow(self._node)
        self._window.show()

        self._node_timer = QTimer(self)
        self._node_timer.timeout.connect(self._spin_node)
        self._node_timer.start()

    def _spin_node(self):
        if rclpy.ok():
            rclpy.spin_once(self._node, timeout_sec=0)


def main():
    app = TactigonMockApp(sys.argv)
    app.exec()
    rclpy.shutdown()


if __name__ == "__main__":
    main()

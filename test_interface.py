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
from enum import Enum

import rclpy
from rclpy.node import Node

from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QPushButton
from PyQt5.QtCore import QTimer

from sunrise_msgs.msg import Intent, Action, BraccioCommand, BraccioResponse

class TestNode(Node):
    def __init__(self):
        Node.__init__(self, "TestNode")

        self.intent_pub = self.create_publisher(Intent, "/sunrise/mission_controller/intent", 10)
        self.action_pub = self.create_publisher(Action, "/sunrise/mission_controller/action", 10)
        self.braccio_pub = self.create_publisher(BraccioCommand, "/braccio_ros/command", 10)
        self.braccio_sub = self.create_subscription(
            BraccioResponse,
            "/braccio_ros/response",
            self.braccio_response_callback,
            10
        )

    @staticmethod
    def get_teach_intent(payload: dict) -> Intent:
        i = Intent()
        i.type = Intent.TEACH
        i.payload = json.dumps(payload)

        return i
    
    @staticmethod
    def get_repeat_intent(payload: dict) -> Intent:
        i = Intent()
        i.type = Intent.REPEAT
        i.payload = json.dumps(payload)

        return i
    
    @staticmethod
    def get_camera_action(x: int, y: int) -> Action:
        a = Action()
        a.type = Action.CAMERA_POINT
        a.payload = json.dumps(dict(x=x, y=y))

        return a
    
    @staticmethod
    def get_braccio_command(x: int, y: int, z: int, gripper: str = "CLOSE", wrist: str = "HORIZONTAL") -> BraccioCommand:
        bc = BraccioCommand()
        bc.x = x
        bc.y = y
        bc.z = z
        bc.gripper_state = gripper
        bc.wrist_state = wrist

        return bc

    def send_intent(self, intent: Intent):
        print("Sending", intent)
        self.intent_pub.publish(intent)

    def send_action(self, action: Action):
        print("Sending", action)
        self.action_pub.publish(action)

    def send_braccio_command(self, command: BraccioCommand):
        print("Sending", command)
        self.braccio_pub.publish(command)

    def braccio_response_callback(self, msg: BraccioResponse):
        self.get_logger().info(
            f"Received Braccio response: {msg}"
        )


class TestWindow(QMainWindow):
    def __init__(self, node: TestNode, parent=None):
        QMainWindow.__init__(self, parent)
        self.setWindowTitle("Sunrise tester App")
        self.resize(1270, 820)

        self._node = node

        self._container = QWidget(self)
        self._layout = QVBoxLayout()
        self._container.setLayout(self._layout)

        self.setCentralWidget(self._container)

    def main_layout(self):
        teach_task_btn = QPushButton("Intent TEACH task", self._container)
        teach_task_btn.clicked.connect(lambda: self._node.send_intent(TestNode.get_teach_intent(dict(task="pick from position stock"))))

        self._layout.addWidget(teach_task_btn)

        teach_pick_btn = QPushButton("Intent TEACH pick", self._container)
        teach_pick_btn.clicked.connect(lambda: self._node.send_intent(TestNode.get_teach_intent(dict(skill="pick"))) )

        self._layout.addWidget(teach_pick_btn)

        position1_btn = QPushButton("Camera Position (100, 100)", self._container)
        position1_btn.clicked.connect(lambda: self._node.send_action(TestNode.get_camera_action(100, 100)))

        self._layout.addWidget(position1_btn)

        teach_place_btn = QPushButton("Intent TEACH place", self._container)
        teach_place_btn.clicked.connect(lambda: self._node.send_intent(TestNode.get_teach_intent(dict(skill="pick"))) )

        self._layout.addWidget(teach_place_btn)

        position2_btn = QPushButton("Camera Position (-100, 100)", self._container)
        position2_btn.clicked.connect(lambda: self._node.send_action(TestNode.get_camera_action(-100, 100)))

        self._layout.addWidget(position2_btn)

        repeat_task_btn = QPushButton("Intent REPEAT task", self._container)
        repeat_task_btn.clicked.connect(lambda: self._node.send_intent(TestNode.get_repeat_intent(dict(task="pick from position stock"))))

        self._layout.addWidget(repeat_task_btn)

        braccio_1_btn = QPushButton("Braccio position (100, 100, 100)", self._container)
        braccio_1_btn.clicked.connect(lambda: self._node.send_braccio_command(TestNode.get_braccio_command(100, 100, 100)))

        self._layout.addWidget(braccio_1_btn)

        braccio_2_btn = QPushButton("Braccio position (100, 100, 0)", self._container)
        braccio_2_btn.clicked.connect(lambda: self._node.send_braccio_command(TestNode.get_braccio_command(100, 100, 0, "OPEN", "VERTICAL")))

        self._layout.addWidget(braccio_2_btn)
        

class TestApp(QApplication):
    def __init__(self, args=[]):
        QApplication.__init__(self, args)

        self._node = TestNode()

        self._window = TestWindow(self._node)
        self._window.main_layout()
        self._window.show()

        self._node_timer = QTimer(self)
        self._node_timer.timeout.connect(self.spin_node)
        self._node_timer.start()

    def spin_node(self):
        if rclpy.ok():
            rclpy.spin_once(self._node, timeout_sec=0)


def main():
    rclpy.init()

    app = TestApp(sys.argv)

    # Start the event loop.
    app.exec()

    rclpy.shutdown()

if __name__ == "__main__":
    main()
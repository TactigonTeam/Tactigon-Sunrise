import sys
import json
from enum import Enum

import rclpy
from rclpy.node import Node

from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QPushButton
from PyQt5.QtCore import QTimer

from sunrise_msgs.msg import Intent, Action


class TestNode(Node):
    def __init__(self):
        Node.__init__(self, "TestNode")

        self.intent_pub = self.create_publisher(Intent, "/sunrise/mission_controller/intent", 10)
        self.action_pub = self.create_publisher(Action, "/sunrise/mission_controller/action", 10)

    @staticmethod
    def get_teach_intent(skill_name: str) -> Intent:
        i = Intent()
        i.type = Intent.TEACH
        i.payload = json.dumps(dict(skill=skill_name))

        return i
    
    @staticmethod
    def get_camera_action(x: int, y: int) -> Action:
        a = Action()
        a.type = Action.CAMERA_POINT
        a.payload = json.dumps(dict(x=x, y=y))

        return a

    def send_intent(self, intent: Intent):
        print("Sending", intent)
        self.intent_pub.publish(intent)

    def send_action(self, action: Action):
        print("Sending", action)
        self.action_pub.publish(action)


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
        teach_intent_btn = QPushButton("Intent TEACH position", self._container)
        teach_intent_btn.setToolTip("Send the TEACH intent")
        teach_intent_btn.clicked.connect(lambda: self._node.send_intent(TestNode.get_teach_intent("position")) )

        self._layout.addWidget(teach_intent_btn)

        position1_btn = QPushButton("Camera Position (100, 100)", self._container)
        position1_btn.setToolTip("Send the Camera action position")
        position1_btn.clicked.connect(lambda: self._node.send_action(TestNode.get_camera_action(100, 100)))

        self._layout.addWidget(position1_btn)
        

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
        rclpy.spin_once(self._node, timeout_sec=0)


def main():
    rclpy.init()

    app = TestApp(sys.argv)

    # Start the event loop.
    app.exec()

    rclpy.shutdown()

if __name__ == "__main__":
    main()
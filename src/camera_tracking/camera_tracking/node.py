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
import cv2
from cv2.aruco import getPredefinedDictionary, detectMarkers, DICT_4X4_50
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from mediapipe.python.solutions.hands import Hands

from sunrise_msgs.msg import Point2D, Marker, MarkerList
from camera_tracking.models import CameraTrackingConfig

class CameraTrakingNode(Node):
    config: CameraTrackingConfig
    red = (0, 0, 255)
    green = (0, 255, 0)
    marker_refresh_rate = 60  # frames

    def __init__(self, config_path: str):
        Node.__init__(self, CameraTrakingNode.__name__)
        self.get_logger().info("Starting Camera Tracking Node...")

        self.config = self.load_config(config_path)

        self.bridge = CvBridge()
        self.hands = Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.finger_tip = None

        self.marker_definition = getPredefinedDictionary(DICT_4X4_50)
        self.marker_refresh_counter = self.marker_refresh_rate
        self.markers = {}

        self.camera_subscription = self.create_subscription(Image, self.config.camera_topic, self.on_image, 10)
        self.camera_pubblisher = self.create_publisher(Image, self.config.tracking_topic, 10)
        self.marker_publisher = self.create_publisher(MarkerList, self.config.marker_tpic, 10)
        self.pointing_publisher = self.create_publisher(Marker, self.config.pointing_topic, 10)

        self.get_logger().info(f"Camera Tracking Node started. Listening on topic: {self.config.camera_topic}")

    def load_config(self, config_path: str) -> CameraTrackingConfig:
        with open(config_path) as cf:
            return CameraTrackingConfig.FromJSON(json.load(cf))
        
    def is_point_in_marker(self, quad, point):
        def sign(p1, p2, p3):
            return (p1[0] - p3[0]) * (p2[1] - p3[1]) - \
                (p2[0] - p3[0]) * (p1[1] - p3[1])

        b1 = sign(point, quad[0], quad[1]) < 0.0
        b2 = sign(point, quad[1], quad[2]) < 0.0
        b3 = sign(point, quad[2], quad[3]) < 0.0
        b4 = sign(point, quad[3], quad[0]) < 0.0

        return ((b1 == b2) and (b2 == b3) and (b3 == b4))

    def on_image(self, msg: Image):
        self.marker_refresh_counter += 1
        is_pointing = None
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            grayscale_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

            if self.marker_refresh_counter >= self.marker_refresh_rate:
                self.marker_refresh_counter = 0
                self.markers = {}
                corners, ids, _ = detectMarkers(grayscale_image, self.marker_definition)
                if ids is not None:
                    for corner, marker_id in zip(corners, ids):
                        self.get_logger().debug(f"Detected marker ID: {marker_id[0]} at corners: {corner}")

                        corner = corner[0].astype(int)
                        self.get_logger().debug(f"Marker corners (int): {corner}")
                        self.markers[marker_id[0]] = corner

                if self.markers:
                    self.marker_publisher.publish(
                        MarkerList(
                            markers=[
                                Marker(
                                    id=int(marker_id),
                                    corners=[Point2D(x=int(c[0]), y=int(c[1])) for c in corner]
                                ) for marker_id, corner in self.markers.items()
                            ]
                        )
                    )
            
            hand_tracking = self.hands.process(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))
            self.finger_tip = None
            
            if hand_tracking.multi_hand_landmarks: # type: ignore
                for hand_landmarks in hand_tracking.multi_hand_landmarks: # type: ignore
                    self.get_logger().debug(f"Hand landmarks: {hand_landmarks}")

                    finger_tip = hand_landmarks.landmark[8]
                    h, w, _ = cv_image.shape

                    x_pixel = int(finger_tip.x * w)
                    y_pixel = int(finger_tip.y * h)

                    self.finger_tip = (x_pixel, y_pixel)

            for marker_id, corner in self.markers.items():
                if self.finger_tip and not is_pointing:
                    is_pointing = Marker(
                        id=int(marker_id),
                        corners=[Point2D(x=int(c[0]), y=int(c[1])) for c in corner]
                    ) if self.is_point_in_marker(corner, self.finger_tip) else None
                # cv2.polylines(cv_image, [corner], isClosed=True, color=self.green, thickness=2)

            if self.finger_tip:
                color = self.green if is_pointing else self.red
                # cv2.circle(cv_image, self.finger_tip, radius=20, color=color, thickness=-1)

            if is_pointing:
                self.pointing_publisher.publish(is_pointing)

            # self.camera_pubblisher.publish(self.bridge.cv2_to_imgmsg(cv_image, encoding='bgr8'))

        except Exception as e:
            self.get_logger().error(f"Errore nella conversione o invio immagine: {e}")

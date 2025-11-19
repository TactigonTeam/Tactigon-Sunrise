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
import math
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
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.is_pointing: Marker | None = None
        self.finger_tip: tuple[int, int] | None = None

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
        
    def is_point_in_marker(self, quad, point) -> bool:
        def sign(p1, p2, p3):
            return (p1[0] - p3[0]) * (p2[1] - p3[1]) - \
                (p2[0] - p3[0]) * (p1[1] - p3[1])
        
        if not point:
            return False

        b1 = sign(point, quad[0], quad[1]) < 0.0
        b2 = sign(point, quad[1], quad[2]) < 0.0
        b3 = sign(point, quad[2], quad[3]) < 0.0
        b4 = sign(point, quad[3], quad[0]) < 0.0

        return ((b1 == b2) and (b2 == b3) and (b3 == b4))
    
    def expand_quad(self, quad, margin):

        expanded = []

        for i in range(4):
            p1 = quad[i]
            p2 = quad[(i + 1) % 4]

            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]

            length = math.hypot(dx, dy)
            nx = -dy / length
            ny = dx / length

            expanded.append((p1[0] + nx * margin, p1[1] + ny * margin))

        return expanded
    
    def is_point_in_marker_with_margin(self, quad, point, margin=0.0) -> bool:
        if margin > 0:
            quad = self.expand_quad(quad, margin)
        return self.is_point_in_marker(quad, point)
    
    def create_marker(self, marker_id: int, corners) -> Marker:
        return Marker(
            id=int(marker_id),
            p1=Point2D(x=int(corners[0][0]), y=int(corners[0][1])),
            p2=Point2D(x=int(corners[1][0]), y=int(corners[1][1])),
            p3=Point2D(x=int(corners[2][0]), y=int(corners[2][1])),
            p4=Point2D(x=int(corners[3][0]), y=int(corners[3][1])),
        )

    def on_image(self, msg: Image):
        self.marker_refresh_counter += 1
        self.is_pointing = None
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            grayscale_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

            if self.marker_refresh_counter >= self.marker_refresh_rate:
                self.marker_refresh_counter = 0

                markers_to_remove = [marker_id for marker_id in self.markers.keys() if not self.is_point_in_marker_with_margin(self.markers[marker_id], self.finger_tip)]

                for marker_id in markers_to_remove:
                    self.markers.pop(marker_id)

                corners, ids, _ = detectMarkers(grayscale_image, self.marker_definition)
                if ids is not None:
                    for corner, marker_id in zip(corners, ids):
                        corner = corner[0].astype(int)
                        self.markers[marker_id[0]] = corner
                
                if self.markers:
                    marker_list = MarkerList(
                        markers=[self.create_marker(marker_id, corner) for marker_id, corner in self.markers.items()]
                    )
                    self.get_logger().debug(f"Detected markers: {marker_list}")
                    self.marker_publisher.publish(marker_list)
                else:
                    self.get_logger().debug("No markers detected.")
            
            hand_tracking = self.hands.process(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))

            self.finger_tip = None
            
            if hand_tracking.multi_hand_landmarks: # type: ignore
                for hand_landmarks in hand_tracking.multi_hand_landmarks: # type: ignore
                    self.get_logger().debug(f"Hand landmarks: {hand_landmarks}")

                    finger_tip_landmark = hand_landmarks.landmark[8]
                    h, w, _ = cv_image.shape

                    x_pixel = int(finger_tip_landmark.x * w)
                    y_pixel = int(finger_tip_landmark.y * h)
                    color = self.red

                    for marker_id, corner in self.markers.items():
                        if self.is_point_in_marker_with_margin(corner, (x_pixel, y_pixel), self.config.marker_detection_margin) and not self.is_pointing:
                            self.is_pointing = self.create_marker(marker_id, corner)
                            self.pointing_publisher.publish(self.is_pointing)
                            self.finger_tip = (x_pixel, y_pixel)
                            color = self.green

                    cv2.circle(cv_image, (x_pixel, y_pixel), radius=20, color=color, thickness=-1)

            for marker_id, corner in self.markers.items():
                cv2.polylines(cv_image, [corner], isClosed=True, color=self.green, thickness=2)

            self.camera_pubblisher.publish(self.bridge.cv2_to_imgmsg(cv_image, encoding='bgr8'))

        except Exception as e:
            self.get_logger().error(f"Errore nella conversione o invio immagine: {e}")

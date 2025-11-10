import cv2
from cv_bridge import CvBridge

from mediapipe.python.solutions.hands import Hands, HAND_CONNECTIONS
from mediapipe.python.solutions.drawing_utils import draw_landmarks, DrawingSpec

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image

class HandTrackingNode(Node):
    hand_tracking_topic: str = "/camera/hand_tracking"
    hand_tracking: Hands

    def __init__(self, camera_topic: str):
        Node.__init__(self, HandTrackingNode.__name__)
        self.bridge = CvBridge()

        self.hand_tracking = Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        self.subscription = self.create_subscription(Image, camera_topic, self.on_image, 10)
        self.publisher = self.create_publisher(Image, self.hand_tracking_topic, 10)

    def on_image(self, msg: Image):
        image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        try:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            result = self.hand_tracking.process(image_rgb)

            if result.multi_hand_landmarks:
                for hand_landmarks in result.multi_hand_landmarks:
                    draw_landmarks(
                        image,
                        hand_landmarks,
                        HAND_CONNECTIONS,
                        DrawingSpec(color=(0, 0, 255), thickness=4, circle_radius=6),
                        DrawingSpec(color=(0, 255, 0), thickness=3),
                    )
                # for hand_landmarks in result.multi_hand_landmarks:
                #     draw_landmarks(image, hand_landmarks, HAND_CONNECTIONS)

        except Exception as e:
            self.get_logger().error(f"Errore nella conversione o invio immagine: {e}")

        msg = self.bridge.cv2_to_imgmsg(image, encoding='bgr8')
        self.publisher.publish(msg)

    def destroy_node(self):
        self.destroy_subscription(self.subscription)
        Node.destroy_node(self)

if __name__ == "__main__":
    rclpy.init()
    node = HandTrackingNode("/camera/image_raw")
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

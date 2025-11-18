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
import rclpy
from rclpy.node import Node
import time
from tactigon_arduino_braccio import Braccio, Wrist, Gripper
from braccio_ros_msgs.msg import BraccioCommand
from braccio_ros_msgs.msg import BraccioResponse

from braccio_ros.models import BraccioConfig

class BraccioRos(Node):
    config: BraccioConfig
    braccio: Braccio

    def __init__(self, config_path: str):
        Node.__init__(self, BraccioRos.__name__)
        self.get_logger().info("Attempting to connect to Braccio...")

        self.config = self.load_config(config_path)
        self.braccio = Braccio(self.config) 
        self.braccio.start()

        for _ in range(100):
            if self.braccio.connected:
                break
            time.sleep(0.1)

        if self.braccio.connected:
            self.get_logger().info("Braccio connected successfully.")
        else:
            self.get_logger().error("Failed to connect to Braccio. Exiting.")                
            rclpy.shutdown()
            return 

        self.move_result_pub = self.create_publisher(
            BraccioResponse, 
            self.config.response_topic,
            10
        )

        self.command_subscriber = self.create_subscription(
            BraccioCommand,
            self.config.command_topic,
            self.command_callback,
            10
        )

        self.get_logger().info(f"Braccio Communication Node started")
        self.get_logger().info(f"Waiting for commands on {self.config.command_topic}")
        self.get_logger().info(f"Response for commands on {self.config.response_topic}")

    def load_config(self, config_path: str) -> BraccioConfig:
        with open(config_path) as cf:
            return BraccioConfig.FromJSON(json.load(cf))

    def command_callback(self, msg: BraccioCommand):
        self.get_logger().info(
            f"Received command: X={msg.x}, Y={msg.y}, Z={msg.z}, "
            f"Wrist='{msg.wrist_state}', Gripper='{msg.gripper_state}'"
        )

        try:
            target_wrist = Wrist[msg.wrist_state.upper()]
        except ValueError:
            self.get_logger().warn(f"Invalid wrist state: '{msg.wrist_state}'. Using HORIZONTAL.")
            target_wrist = Wrist.HORIZONTAL

        try:
            target_gripper = Gripper[msg.gripper_state.upper()]
        except ValueError:
            self.get_logger().warn(f"Invalid gripper state: '{msg.gripper_state}'. Using CLOSE.")
            target_gripper = Gripper.CLOSE

        if not self.braccio.connected:
            self.get_logger().error("Braccio is not connected. Cannot execute move.")
            # Optionally publish a failure response
            response_msg = BraccioResponse()
            response_msg.success = False
            response_msg.status = "Braccio not connected"
            response_msg.move_time = 0.0
            self.move_result_pub.publish(response_msg)
            return

        # Execute the move
        try:
            res, status, move_time = self.braccio.move(
                msg.x, msg.y, msg.z, target_wrist, target_gripper
            )

            # Publish move result
            response_msg = BraccioResponse()
            response_msg.success = bool(res)
            response_msg.status = str(status)
            response_msg.move_time = float(move_time)
            self.move_result_pub.publish(response_msg)

            if res:
                self.get_logger().info(f"Move successful -> status: {status}, t: {move_time:.2f}s")
            else:
                self.get_logger().warn(f"Braccio move failed. Status: {status}")
        except Exception as e:
            self.get_logger().error(f"Exception during braccio.move: {e}")
            response_msg = BraccioResponse()
            response_msg.success = False
            response_msg.status = f"Exception: {e}"
            response_msg.move_time = 0.0
            self.move_result_pub.publish(response_msg)


    def destroy_node(self):
        self.get_logger().info("Shutting down Braccio Simple Controller Node...")
        if self.braccio and self.braccio.connected:
            self.get_logger().info("Sending Braccio to home position...")
            try:
                self.braccio.home()
            except Exception as e:
                self.get_logger().warn(f"Could not send Braccio to home: {e}")
            finally:
                self.get_logger().info("Cleaning up Braccio connection...")
                self.braccio.stop(5)
        Node.destroy_node(self)
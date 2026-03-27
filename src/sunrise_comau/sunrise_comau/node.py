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
from rclpy.action import ActionClient
from rclpy.logging_service import LoggingSeverity

from action_msgs.msg import GoalStatus
from comau_msgs.action import ExecuteJointTrajectory
from comau_msgs.msg import ActionResult
from braccio_ros_msgs.msg import BraccioJointCommand

from sunrise_comau.models import ComauConfig

class ComauRos(Node):
    config: ComauConfig
    online: bool

    def __init__(self, config_path: str):
        Node.__init__(self, ComauRos.__name__)
        self.get_logger().set_level(LoggingSeverity.DEBUG)
        self.get_logger().info("Attempting to connect to Comau...")

        self.bool = False
        self.config = self.load_config(config_path)
        self._client = ActionClient(
            self,
            ExecuteJointTrajectory,
            '/execute_joint_trajectory_handler'
        )

        if not self._client.wait_for_server(timeout_sec=5):
            self.get_logger().error('Joint action server not available after 5s')
            rclpy.shutdown()
            return

        self.get_logger().debug(f"Create response topic {self.config.response_topic}")
        self.move_result_pub = self.create_publisher(
            ActionResult, 
            self.config.response_topic,
            10
        )

        self.get_logger().debug(f"Create command topic {self.config.command_topic}")
        self.command_subscriber = self.create_subscription(
            BraccioJointCommand,
            self.config.command_topic,
            self.command_callback,
            10
        )

        self.get_logger().info(f"Braccio Communication Node started")
        self.get_logger().info(f"Waiting for commands on {self.config.command_topic}")
        self.get_logger().info(f"Response for commands on {self.config.response_topic}")

    def load_config(self, config_path: str) -> ComauConfig:
        with open(config_path) as cf:
            return ComauConfig.FromJSON(json.load(cf))

    def command_callback(self, msg: BraccioJointCommand):
        self.get_logger().info(
            f"Received command: {msg}"
        )
        
        goal = ExecuteJointTrajectory.Goal(
            trajectory=msg.trajectory
        )
        goal_future = self._client.send_goal_async(goal, feedback_callback=self.feedback)
        goal_future.add_done_callback(self.done_callback)

    def feedback(self, feedback):
        self.get_logger().info(f"Feedback: {feedback}")

    def done_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Joint goal was rejected by server')
            self.move_result_pub.publish(
               ActionResult(
                   success=False,
                   status="Cancelled"
               ) 
            )
            return
        self.get_logger().info('Joint goal accepted, waiting for result...')
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.send_results)

    def send_results(self, future):
        result = future.result()
        status = result.status
        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().warn('Joint trajectory SUCCEEDED!')
            self.move_result_pub.publish(
               ActionResult(
                   success=True,
                   status="Success"
               ) 
            )
        elif status == GoalStatus.STATUS_ABORTED:
            self.get_logger().error('Joint goal was ABORTED')
            self.move_result_pub.publish(
               ActionResult(
                   success=False,
                   status="EmergencyStop"
               ) 
            )
        elif status == GoalStatus.STATUS_CANCELED:
            self.get_logger().error('Joint goal was CANCELED')
            self.move_result_pub.publish(
               ActionResult(
                   success=False,
                   status="Cancelled"
               ) 
            )
        else:
            self.get_logger().error(f'Unknown result status: {status}')
            self.move_result_pub.publish(
               ActionResult(
                   success=False,
                   status="OperationalException"
               ) 
            )

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
#!/usr/bin/env python3
"""
comau_example_client.py
Equivalente Python di execute_example_node.cpp + ex_trj_handler.cpp
Invia traiettorie cartesiane e/o joint al robot COMAU via action server.

Uso:
    # Traiettoria joint:
    python3 comau_example_client.py --joints

    # Traiettoria cartesiana:
    python3 comau_example_client.py --cart

    # Entrambe in sequenza:
    python3 comau_example_client.py --joints --cart
"""

import sys
import argparse
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.task import Future

from comau_msgs.action import ExecuteJointTrajectory, ExecuteCartesianTrajectory
from comau_msgs.msg import JointPose, CartesianPoseStamped
from std_msgs.msg import Header


# ── Traiettoria cartesiana di esempio ────────────────────────────────────────
# Stessa sequenza di send_goal() nel C++ originale (in metri e radianti)
CARTESIAN_WAYPOINTS = [
    # x      y       z      roll   pitch  yaw
    (0.436,  0.000,  0.705, 3.140, 0.000, 3.140),  # HOME
    (0.436,  0.143,  0.589, 3.140, 0.000, 3.140),  # first
    (0.608,  0.143,  0.589, 3.140, 0.000, 3.140),  # second
    (0.608, -0.143,  0.589, 3.140, 0.000, 3.140),  # third
    (0.436, -0.143,  0.585, 3.140, 0.000, 3.140),  # fourth
    (0.436,  0.143,  0.589, 3.140, 0.000, 3.140),  # first (ripetuto)
    (0.436,  0.143,  0.400, 3.140, 0.000, 3.140),  # fifth
    (0.608,  0.143,  0.400, 3.140, 0.000, 3.140),  # sixth
    (0.608, -0.143,  0.400, 3.140, 0.000, 3.140),  # seventh
    (0.436, -0.143,  0.400, 3.140, 0.000, 3.140),  # eighth
    (0.436,  0.143,  0.400, 3.140, 0.000, 3.140),  # fifth (ripetuto)
    (0.436,  0.000,  0.705, 3.140, 0.000, 3.140),  # HOME
]

# ── Traiettoria joint di esempio ──────────────────────────────────────────────
# Stessa sequenza di send_jnt_goal() nel C++ originale (in radianti)
# Filtro originale: |deg| < 180  →  tutti questi valori passano il filtro

# header:
#   stamp:
#     sec: 1774520726
#     nanosec: 803332928
#   frame_id: ''
# name:
# - joint_1
# - joint_2
# - joint_3
# - joint_4
# - joint_5
# - joint_6
# - joint_7
# position:
# - -0.0023441987577825785
# - -0.5219180583953857
# - -1.5717942714691162
# - -8.168862405000255e-05
# - 1.137688159942627
# - 0.002424167701974511
# - 0.0
# velocity: []
# effort: []

# JOINT_WAYPOINTS = [
#     [ 0.436332, 0.0, -1.5708, 0.0, 1.57, 0.0],
#     [-0.436332, 0.0, -1.5708, 0.0, 1.57, 0.0],
#     [ 0.0,      0.0, -1.5708, 0.0, 1.57, 0.0],
# ]

JOINT_WAYPOINTS = [
    # [ 0.0, -0.5, -1.5708, 0.0, 1.1, 0.0, 0.0, 0.0, 0.0],
    # [ -0.5, 0.0, -1.5708, 0.0, 1.1, 0.0, 0.0, 0.0, 0.0],
    [ -0.0, 0.0, -1.5708, 0.0, 1.1, 0.0, 0.0, 0.0, 0.0],
    # [ 0.0, -0.5, -1.5708, 0.0, 1.1, 0.0, 0.0, 0.0, 0.0],
    # [ 0.0, 0.0, -1.5708, 0.0, 1.1, 0.0, 0.0],
    # [ 0.0, 0.0, -1.5708, 0.0, 1.1, 0.0, 0.0],
]

MAX_ABS_DEG = 180.0  # filtro del C++ originale


class ComauExampleClient(Node):

    def __init__(self):
        super().__init__('comau_example_client')

        # Action client per traiettorie cartesiane
        self._cart_client = ActionClient(
            self,
            ExecuteCartesianTrajectory,
            'execute_cartesian_trajectory_handler'
        )

        # Action client per traiettorie joint
        self._jnt_client = ActionClient(
            self,
            ExecuteJointTrajectory,
            'execute_joint_trajectory_handler'
        )

    # ── Traiettoria cartesiana ────────────────────────────────────────────────

    def send_cartesian_trajectory(self) -> bool:
        self.get_logger().warn('Sending Cartesian Trajectory...')

        if not self._cart_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error('Cartesian action server not available after 5s')
            return False

        self.get_logger().warn('Cartesian action server available')

        goal = ExecuteCartesianTrajectory.Goal()
        header = Header()
        header.frame_id = 'base_link'

        for x, y, z, roll, pitch, yaw in CARTESIAN_WAYPOINTS[:1]:
            pose = CartesianPoseStamped()
            pose.header     = header
            pose.x          = x
            pose.y          = y
            pose.z          = z
            pose.roll       = roll
            pose.pitch      = pitch
            pose.yaw        = yaw
            pose.move_type  = 'joint'
            goal.trajectory.append(pose)

        self.get_logger().info(f'Sending {goal}')

        self.get_logger().info(f'Sending {len(goal.trajectory)} cartesian waypoints')

        send_goal_future = self._cart_client.send_goal_async(
            goal,
            feedback_callback=self._cart_feedback_callback
        )
        send_goal_future.add_done_callback(self._cart_goal_response_callback)
        return True

    def _cart_goal_response_callback(self, future: Future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Cartesian goal was rejected by server')
            return
        self.get_logger().info('Cartesian goal accepted, waiting for result...')
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self._cart_result_callback)

    def _cart_feedback_callback(self, feedback_msg):
        fb = feedback_msg.feedback
        self.get_logger().info(f'FEEDBACK: {fb.action_feedback.success}')

    def _cart_result_callback(self, future: Future):
        result = future.result()
        status = result.status
        from action_msgs.msg import GoalStatus
        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().warn('Cartesian trajectory SUCCEEDED!')
        elif status == GoalStatus.STATUS_ABORTED:
            self.get_logger().error('Cartesian goal was ABORTED')
        elif status == GoalStatus.STATUS_CANCELED:
            self.get_logger().error('Cartesian goal was CANCELED')
        else:
            self.get_logger().error(f'Unknown result status: {status}')

    # ── Traiettoria joint ─────────────────────────────────────────────────────

    def send_joint_trajectory(self) -> bool:
        self.get_logger().warn('Sending Joint Trajectory...')

        if not self._jnt_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error('Joint action server not available after 5s')
            return False

        self.get_logger().warn('Joint action server available')

        goal = ExecuteJointTrajectory.Goal()

        for waypoint in JOINT_WAYPOINTS:
            pose = JointPose()
            pose.positions = [
                q for q in waypoint
                # Stesso filtro del C++ originale: |deg| < 180
                if abs(q * 180.0 / 3.14159265) < MAX_ABS_DEG
            ]
            goal.trajectory.append(pose)

        self.get_logger().info(f'Sending {len(goal.trajectory)} joint waypoints')

        send_goal_future = self._jnt_client.send_goal_async(
            goal,
            feedback_callback=self._jnt_feedback_callback
        )
        send_goal_future.add_done_callback(self._jnt_goal_response_callback)
        return True

    def _jnt_goal_response_callback(self, future: Future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Joint goal was rejected by server')
            return
        self.get_logger().info('Joint goal accepted, waiting for result...')
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self._jnt_result_callback)

    def _jnt_feedback_callback(self, feedback_msg):
        fb = feedback_msg.feedback
        self.get_logger().info(f'FEEDBACK: {fb.action_feedback.success}')

    def _jnt_result_callback(self, future: Future):
        result = future.result()
        status = result.status
        from action_msgs.msg import GoalStatus
        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().warn('Joint trajectory SUCCEEDED!')
        elif status == GoalStatus.STATUS_ABORTED:
            self.get_logger().error('Joint goal was ABORTED')
        elif status == GoalStatus.STATUS_CANCELED:
            self.get_logger().error('Joint goal was CANCELED')
        else:
            self.get_logger().error(f'Unknown result status: {status}')


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='COMAU ROS2 example trajectory client (Python)'
    )
    parser.add_argument('--joints', action='store_true',
                        help='Invia traiettoria joint (execute_joint_trajectory_handler)')
    parser.add_argument('--cart',   action='store_true',
                        help='Invia traiettoria cartesiana (execute_cartesian_trajectory_handler)')
    args = parser.parse_args()

    if not args.joints and not args.cart:
        parser.print_help()
        sys.exit(0)

    rclpy.init()
    node = ComauExampleClient()

    try:
        if args.joints:
            node.send_joint_trajectory()

        if args.cart:
            node.send_cartesian_trajectory()

        # Spin finché ci sono callback in attesa (goal response + result)
        rclpy.spin(node)

    except KeyboardInterrupt:
        node.get_logger().warn('Interrupted by user, shutting down.')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
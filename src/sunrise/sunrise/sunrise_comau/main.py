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
import rclpy
from rclpy.logging import get_logger
from rclpy.executors import MultiThreadedExecutor

from sunrise.sunrise_comau.node import ComauRos

def main(args=None):
    config_path = sys.argv[1] if len(sys.argv) > 1 else None

    if not config_path:
        get_logger(ComauRos.__name__).error("Cannot start ComauRos node. Config file path is missing")
        return
    
    spin_node(config_path, args)


def spin_node(config_path: str, args=None):
    rclpy.init(args=args)

    node = ComauRos(config_path)
    executor = MultiThreadedExecutor()

    try:
        executor.add_node(node)
        executor.spin()
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.try_shutdown()
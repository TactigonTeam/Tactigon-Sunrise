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

import argparse
from sunrise_app import Server

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Sunrise App")
    parser.add_argument("-A", "--address", help="Server address", type=str, default="0.0.0.0")
    parser.add_argument("-P", "--port", help="Server port", type=int, default=5123)
    args = parser.parse_args()

    server = Server(args.address, args.port)
    try:
        server.serve()
    except KeyboardInterrupt:
        server.stop()
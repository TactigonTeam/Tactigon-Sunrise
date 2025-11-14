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
#********************************************************************************/

from platform import system

platform_name = system()
__version__ = f"5.4.0.0"

import sys
import requests
import logging
import time
from os import path
from multiprocessing import Event, Process, Queue
from flask import Flask, render_template, send_from_directory, request
from gevent.pywsgi import WSGIServer

from typing import Optional

from sunrise_app.config import app_config
from sunrise_app.models import BASE_PATH

from sunrise_app.modules.shapes.extension import ShapesApp
from sunrise_app.modules.zion.extension import ZionInterface
from sunrise_app.modules.zion.manager import get_zion_interface
from sunrise_app.modules.ros2.extension import Ros2Interface
from sunrise_app.modules.ros2.manager import get_ros2_interface

class Server(Process):
    url: str
    port: int
    debug: bool

    def __init__(self, url: str = "localhost", port: int = 5000, debug: bool = False):
        Process.__init__(self)
        self.url = url
        self.port = port
        self.debug = debug
        self._ready_flag = Event()

    @property
    def address(self) -> str:
        return F"http://{self.url}:{self.port}"
    
    @property
    def ready(self) -> bool:
        return self._ready_flag.is_set()
    
    def serve(self):
        print(F"Serving application on {self.address}, port {self.port}")
        self.start()

        while not self._ready_flag.is_set():
            time.sleep(0.5)

        input("Type any key to exit...\n")
    
        self.stop()
        self.terminate()

    def run(self):
        logging.getLogger("bleak").setLevel(logging.INFO)
        app = self.create_app(self.debug)
        server = WSGIServer((self.url, self.port), app)
        self._ready_flag.set()
        server.serve_forever()

    def create_app(self, debug: bool = False):
        flask_app = Flask(__name__, template_folder="templates", static_folder="static")
        flask_app.config.from_object(app_config)

        with flask_app.app_context():

            shapes_app = ShapesApp(path.join(BASE_PATH, "config", "shapes"))
            zion_interface = ZionInterface(path.join(BASE_PATH, "config", "zion"))
            ros2_interface = Ros2Interface(path.join(BASE_PATH, "config", "ros2"))

            flask_app.debug = debug
            zion_interface.init_app(flask_app)
            shapes_app.init_app(flask_app)
            ros2_interface.init_app(flask_app)

            shapes_app.zion_interface = zion_interface
            shapes_app.ros2_interface = ros2_interface

            from . import main
            from .modules.shapes.blueprint import bp as shapes_bp
            from .modules.zion.blueprint import bp as zion_bp
            from sunrise_app.modules.ros2.blueprint import bp as ros2_bp

            flask_app.register_blueprint(main.bp)
            flask_app.register_blueprint(shapes_bp)
            flask_app.register_blueprint(zion_bp)
            flask_app.register_blueprint(ros2_bp)

            @flask_app.route('/favicon.ico')
            def favicon():
                return send_from_directory(path.join(flask_app.root_path, "static", "images"), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

            @flask_app.errorhandler(Exception)
            def handle_exception(e):
                # now you're handling non-HTTP exceptions only
                print("Error:", e)
                return render_template("error.jinja", error=e, url=request.url, method=request.method, args=request.args, form=request.form), 500

            @flask_app.context_processor
            def inject_data():
                zion_interface = get_zion_interface()
                ros2_inferface = get_ros2_interface()

                if zion_interface:
                    zion_config = zion_interface.config
                else:
                    zion_config = None

                has_ros2 = ros2_inferface is not None

                return dict(
                    DEBUG=app_config.DEBUG,
                    BASE_PATH=BASE_PATH,
                    platform=sys.platform,
                    request_path=request.path,
                    zion_config=zion_config,
                    has_ros2=has_ros2,
                )

        return flask_app
    
    def stop(self):
        return requests.get(F"{self.address}/quit").status_code == 200

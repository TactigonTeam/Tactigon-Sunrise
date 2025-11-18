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

from threading import Thread, Event
from flask import Flask
from flask_socketio import SocketIO

from typing import Optional

from sunrise_app.modules.shapes.extension import ShapesApp

class SocketApp(SocketIO):
    name: str = "socket_app"
    _TICK: float = 0.02
    socket_thread: Optional[Thread]
    _stop_event: Event
    _shapes_app: Optional[ShapesApp] = None

    def __init__(self, app: Optional[Flask] = None, **kwargs):
        SocketIO.__init__(self, app, async_mode="gevent", cors_allowed_origins="*", **kwargs)

        self.socket_thread = None
        self._stop_event = Event()

        if app:
            self.init_app(app)

    def init_app(self, app: Flask, *args, **kwargs):
        SocketIO.init_app(self, app, *args, **kwargs)
        app.extensions[self.name] = self

    @property
    def is_running(self) -> bool:
        return not self._stop_event.is_set()

    @property
    def shapes_app(self) -> Optional[ShapesApp]:
        """
        Get the Shapes App reference

        :return: Shapes App if present
        """

        return self._shapes_app
    
    @shapes_app.setter
    def shapes_app(self, app: ShapesApp) -> None:
        """
        Set the Shapes App reference

        :app: Shapes App
        """
        self._shapes_app = app

    def start(self):
        """
        Start socket thread
        """
        self._stop_event.clear()
        self.socket_thread = self.start_background_task(self.socket_emit_function)

    def stop(self):
        """
        Stop socket thread
        """
        self._stop_event.set()

    def socket_emit_function(self):
        while not self._stop_event.is_set():
            if self._shapes_app and self._shapes_app.is_running:
                msg = self._shapes_app.get_log()
                if msg:
                    self.emit("logging", msg.toJSON())
                
            self.sleep(SocketApp._TICK)  # type: ignore
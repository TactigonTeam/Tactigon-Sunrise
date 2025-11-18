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

import time
from abc import ABC, abstractmethod
from threading import Thread, Event
from typing import Optional, Any

from flask import Flask


class ExtensionThread(ABC, Thread):
    TICK: float = 0.02
    _stop_event: Event

    def __init__(self):
        Thread.__init__(self, daemon=False)
        self._stop_event = Event()

    def run(self):
        while not self._stop_event.is_set():
            self.main()
            time.sleep(self.TICK)

    @abstractmethod
    def main(self):
        pass

    @property
    def is_running(self) -> bool:
        return not self._stop_event.is_set() and self.is_alive()

    def start(self):
        self._stop_event.clear()
        Thread.start(self)

    def stop(self):
        self._stop_event.set()
        Thread.join(self)


class ExtensionApp(ABC):
    _thread: Optional[ExtensionThread] = None

    def __init__(self, flask_app: Optional[Flask] = None):
        if flask_app:
            self.init_app(flask_app)

    def init_app(self, flask_app: Flask):
        flask_app.extensions[self.name] = self

    @property
    def name(self) -> str:
        return type(self).__name__

    @property
    def thread(self) -> Optional[ExtensionThread]:
        return self._thread

    @thread.setter
    def thread(self, thread: Optional[ExtensionThread]):
        self._thread = thread

    @property
    def is_running(self) -> bool:
        if self._thread:
            return self._thread.is_running

        return False

    @abstractmethod
    def start(self, *args, **kwargs) -> Any:
        pass

    def stop(self):
        if self.is_running and self.thread:
            self.thread.stop()
            if self.thread.is_alive():
                self.thread.join(0.5)

        self.thread = None
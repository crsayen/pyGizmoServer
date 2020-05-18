"""This module contains the base class that controller classes inherit from.

"""
import json
import asyncio
from pathlib import Path, PureWindowsPath, PurePosixPath
from typing import overload, List, Any
import os
import sys
from sys import platform
from os import path


class Controller(object):
    """This is the base Controller class.

    A controller package is comprised of a schema, and a controller class.
    This is the base class that your controller must inherit from.

    Attributes:
        running: A flag that indicates whether the handlerloop is running.
        callback: The callback is invoked whenever the controller needs to
                  send a Websocket message to the client. The callback will
                  be provided automatically by the main app. You should not
                  assign anything to the callback.
        schema: A Dict representation of the controller's schema file.
    """

    def __init__(self):
        self.i_running = False
        self.i_callback = None
        self.i_coros = []
        bundle_dir = getattr(sys, "_MEIPASS", path.abspath(path.dirname(__file__)))
        # when bundled, the controller runs in it's own directory as opposed to the app's root
        if sys.platform == "win32":
            if bundle_dir.split("\\")[-1].upper() == "PYGIZMOSERVER":
                bundle_dir = (
                    f"{PureWindowsPath(bundle_dir).parent}\\{self.__class__.__name__}"
                )
            with open(f"{bundle_dir}\\schema.json") as f:
                self.i_schema = json.load(f)
        elif sys.platform = "linux":
            if bundle_dir.spit('/')[-1].upper() == "PYGIZMOSERVER":
                bundle_dir = (
                    f"{PurePosixPath(bundle_dir).parent}/{self.__class__.__name__}"
                )
            with open(f"{bundle_dir}/schema.json") as f:
                self.i_schema = json.load(f)

    async def i_handlerloop(self) -> None:
        """Runs for the lifetime of the application, calling Controller.handler.

        This loop will continuously call the handler function that you define.
        handlerloop is called automatically by the application.
        """
        while 1:
            await self.do()
            await asyncio.sleep(0)

    def start(self) -> None:
        """Checks for a user-defined setup function, and calls it if it exists.

        start is called automatically by the application.

        Raises:
            RuntimeError: controller callback not set
        """
        if self.i_callback is None:
            raise RuntimeError("controller callback not set")
        if hasattr(self, "setup"):
            self.setup()

    def spawnPeriodicTask(self, func, args=[], period=1):
        self.i_coros.append(
            {"running": False, "func": func, "args": args, "period": period}
        )

    async def i_tend(self, func: callable, args) -> None:
        """Checks Controller.running, spawns Controller.handlerloop if not.
            also starts any coroutines added with spawnPeriodicTask

        tend is called automatically by the application after every requests.
        """
        if not self.i_running:
            await func(args, self.i_handlerloop())
        for coro in self.i_coros:
            if not coro["running"]:
                await func(
                    args,
                    self.i_callPeriodically(coro["func"], coro["args"], coro["period"]),
                )
                coro["running"] = True
        self.i_running = True

    async def i_callPeriodically(self, func, args=[], period=1):
        while 1:
            await func(*args)
            await asyncio.sleep(period)

    def i_setcallback(self, callback: callable):
        """Sets the Controller.callback.

        setcallback is called automatically by the application.

        Args:
            callback: The function to call when Controller.send is called.

        Raises:
            ValueError: callback must be a funtion.
        """
        if not callable(callback):
            raise ValueError("callback must be a function")
        self.i_callback = callback

    async def do(self):
        """Called continuously during the lifetime of the application.

        do is intended to be used as a coroutine, running concurrently
        with the rest of your code. Use it to poll inputs, provide realtime
        feedback, or any background tasks.

        Children of Controller must implement do. If no do is
        required, use 'pass' for the method's body.
        """
        raise NotImplementedError

    def finished_processing_request(self):
        """Called when the application is finished processing an HTTP request.

        Use as a signal that the application is finished asking for stuff.
        wrap up your task.

        Children of Controller must implement finished_processing_request. If not
        used, use 'pass' for the method's body.
        """
        raise NotImplementedError

    def send(self, path: str = None, data: Any = None, updates: List = None) -> None:
        """Sends a websocket message to the client, with the specified path and data.

        Args:
            path:
                The path the data belongs in. Only required if 'updates' is not passed.
            data:
                The data at the path. Only required if 'updates' is not passed.
            updates:
                A list of {"path":path, "data":data} dicts to send.
        """
        if updates is not None:
            self.i_callback(updates)
            return
        self.i_callback({"path": path, "data": data})

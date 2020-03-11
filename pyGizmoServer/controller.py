"""This module contains the base class that controller classes inherit from.

"""
import json
import asyncio
from typing import overload, List, Any


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
        self.running = False
        self.callback = None
        with open(f"{self.__class__.__name__}/schema.json") as f:
            self.schema = json.load(f)

    async def handlerloop(self) -> None:
        """Runs for the lifetime of the application, calling Controller.handler.

        This loop will continuously call the handler function that you define.
        handlerloop is called automatically by the application.
        """
        while 1:
            await self.handler()
            await asyncio.sleep(0)

    def start(self) -> None:
        """Checks for a user-defined setup function, and calls it if it exists.

        start is called automatically by the application.

        Raises:
            RuntimeError: controller callback not set
        """
        if self.callback is None:
            raise RuntimeError("controller callback not set")
        if hasattr(self, 'setup'):
            self.setup()

    async def tend(self, func: callable, args) -> None:
        """Checks Controller.running, spawns Controller.handlerloop if not.

        tend is called automatically by the application.
        """
        if not self.running:
            await func(args, self.handlerloop())
        self.running = True

    def setcallback(self, callback: callable):
        """Sets the Controller.callback.

        setcallback is called automatically by the application.

        Args:
            callback: The function to call when Controller.send is called.

        Raises:
            ValueError: callback must be a funtion.
        """
        if not callable(callback):
            raise ValueError("callback must be a function")
        self.callback = callback

    async def handler(self):
        """Called continuously during the lifetime of the application.

        handler is intended to be used as a coroutine, running concurrently
        with the rest of your code. Use it to poll inputs, provide realtime
        feedback, or anything else that would otherwise require concurrency.

        Children of Controller must implement handler. If no handling is
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
            self.callback(updates)
            return
        self.callback({
            "path": path,
            "data": data
        })

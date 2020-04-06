import sys
import time
import importlib
import json
import asyncio
from pyGizmoServer.utility import loadconfig, \
    makeresolver, debug, setuplog, ensurelist, Error
from pyGizmoServer.subscription_server import SubscriptionServer
from aiohttp import web
from aiojobs.aiohttp import setup
from aiojobs.aiohttp import spawn
from typing import List, Dict, Tuple, Optional, Union

WATCHING_PULSE = False

async def handlepatch(request: web.Request) -> web.Response:
    """Handles incoming PATCH/POST requests from the client.

    Arguments:
        request {web.Request} -- Passed in by aiohttp, the client's request

    Returns:
        web.Response -- Either some path/data, or an error.
    """
    await controller.tend(spawn, request)
    patchlist: List[Dict[str, any]] = ensurelist(json.loads(await request.text()))
    debug(patchlist)
    response: List = []
    for patch in patchlist:
        path, value = patch.get("path"), patch.get("value")
        props: Dict[str, str] = resolver(path)
        if not (
            props and value is not None and hasattr(controller, props.get("$write"))
        ):
            return Error(f"bad request - {patch}").get_response()
        result = getattr(controller, props["$write"])(*(props["$args"] + [value]))
        if result is None:
            response.append({"path": path, "data": value})
        elif isinstance(result, Error):
            return result.get_response()
    controller.finished_processing_request()
    return web.json_response(response)


async def handleget(request: web.Request) -> web.Response:
    """Handles GET requests from the client.

        If the controller names a GET function for this particular
        path, this will call that function and respond with it's return
        value.

    Arguments:
        request {web.Request} -- Passed in by aiohttp. The client's request

    Returns:
        web.Response -- path/data if the controller provides a GET function,
                        else an error.
    """
    debug(request.path)
    await controller.tend(spawn, request)
    props: Dict[str, str] = resolver(request.path)
    if props and (props.get("$read") or props.get("$watchable")):
        data = await getattr(controller, props["$read"])(*props.get("$args"))
        if isinstance(data, Error):
            return data.get_response()
        response = [{
            "path": request.path,
            "data": data
        }]
    else:
        return Error(f"bad request - {request.path}").get_response()
    return web.json_response(response)


def handleupdates(updates: Union[Dict[str, any], List[Dict[str, any]], Error]) -> None:
    """Receives updates from the controller, and sends them to subscription
        server to be sent to subscribers.

    Arguments:
        updates {Union[Dict[str, any], List[Dict[str, any]], Error]} -- path/data
                updates from the controller
    """
    debug(updates)
    updates = ensurelist(updates)
    for update in updates:
        data, path = update.get("data"), update.get("path")
        subscription_server.publish({"path": path, "value": data})


async def get_schema(request: web.Request) -> web.Response:
    debug(request.path)
    response: Dict[str, Dict] = controller.schema.copy()
    response["wsurl"] = cfg.ws.url
    response["controller"] = controller.__class__.__name__
    return web.json_response(response)


async def get_index(request: web.Request) -> web.Response:
    return web.FileResponse("./dist/index.html")


async def get_favicon(request: web.Request) -> web.Response:
    return web.FileResponse("./dist/favicon.ico")


async def start_heartbeat(request: web.Request) -> web.Response:
    global WATCHING_PULSE
    if not WATCHING_PULSE:
        WATCHING_PULSE = True
        await controller.tend(spawn, request)
        await spawn(request, watch_pulse())
    return web.json_response({"path": "/heartbeat", "data": True})


async def watch_pulse():
    req = {"path": "/heartbeat", "data": 0}
    while True:
        await asyncio.sleep(1)
        if await controller.heartbeat():
            req["data"] += 1
            handleupdates(req)


def make_app() -> web.Application:
    controller.start()
    app = web.Application()
    app["static_root_url"] = "/src"
    app.router.add_get("/", get_index)
    app.router.add_get("/FAVICON", get_favicon)
    app.router.add_static("/js", path="./dist/js")
    app.router.add_static("/css", path="./dist/css")
    app.router.add_route("GET", "/schema", get_schema)
    app.router.add_route("GET", "/heartbeat", start_heartbeat)
    app.router.add_route("GET", r"/{tail:.*}", handleget)
    app.router.add_route("PATCH", r"/{tail:.*}", handlepatch)
    app.router.add_route("POST", r"/{tail:.*}", handlepatch)
    setup(app)
    return app


def main():
    try:
        print(time.asctime(), f"Server started - {cfg.tcp.ip}:{cfg.tcp.port}")
        web.run_app(make_app(), host=cfg.tcp.ip, port=cfg.tcp.port, access_log=None)
    except KeyboardInterrupt:
        sys.exit()

cfg_filename = sys.argv[1] if sys.argv[1:] else "production"
cfg: Dict[str, any] = loadconfig(cfg_filename)
setuplog(cfg)
if cfg is None:
    print(f"\nconfiguration not found\nexiting...\n")
    sys.exit()
subscription_server: SubscriptionServer = SubscriptionServer(cfg.ws.ip, cfg.ws.port)
controller = getattr(
    importlib.import_module(f"{cfg.controller}.{cfg.controller}"), cfg.controller
)()
resolver: callable = makeresolver(controller.schema)
controller.setcallback(handleupdates)


if __name__ == "__main__":
    main()

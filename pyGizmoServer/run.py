import sys
from sys import platform
import time
import importlib
import json
import asyncio
from pyGizmoServer.utility import (
    loadconfig,
    makeresolver,
    debug,
    setuplog,
    ensurelist,
    Error
)
from pyGizmoServer.subscription_server import SubscriptionServer
from aiohttp import web
from aiojobs.aiohttp import setup
from aiojobs.aiohttp import spawn
from typing import List, Dict, Tuple, Optional, Union
from pathlib import Path, PureWindowsPath, PurePosixPath
import os
from os import path

WATCHING_PULSE = False

bundle_dir = getattr(sys, "_MEIPASS", path.abspath(path.dirname(__file__)))
# when bundled, run.py runs in it's own directory as opposed to the app's root
if sys.platform == "win32":
    if bundle_dir.split("\\")[-1].upper() == "PYGIZMOSERVER":
        bundle_dir = PureWindowsPath(bundle_dir).parent
else:
    if bundle_dir.split('/')[-1].upper() == "PYGIZMOSERVER":
        bundle_dir = PurePosixPath(bundle_dir).parent

# def realname(path, root=None):
#     if root is not None:
#         path=os.path.join(root, path)
#     result=os.path.basename(path)
#     if os.path.islink(path):
#         realpath=os.readlink(path)
#         result= '%s -> %s' % (os.path.basename(path), realpath)
#     return result

# def ptree(startpath, depth=-1):
#     prefix=0
#     if startpath != '/':
#         if startpath.endswith('/'): startpath=startpath[:-1]
#         prefix=len(startpath)
#     for root, dirs, files in os.walk(startpath):
#         level = root[prefix:].count(os.sep)
#         if depth >-1 and level > depth: continue
#         indent=subindent =''
#         if level > 0:
#             indent = '|   ' * (level-1) + '|-- '
#         subindent = '|   ' * (level) + '|-- '
#         print('{}{}/'.format(indent, realname(root)))
#         # print dir only if symbolic link; otherwise, will be printed as root
#         for d in dirs:
#             if os.path.islink(os.path.join(root, d)):
#                 print('{}{}'.format(subindent, realname(d, root=root)))
#         for f in files:
#             print('{}{}'.format(subindent, realname(f, root=root)))

# #ptree(bundle_dir)


async def handlepatch(request: web.Request) -> web.Response:
    """Handles incoming PATCH/POST requests from the client.

    Arguments:
        request {web.Request} -- Passed in by aiohttp, the client's request

    Returns:
        web.Response -- Either some path/data, or an error.
    """
    await controller.i_tend(spawn, request)
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
        else:
            response.append(result)
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
    await controller.i_tend(spawn, request)
    props: Dict[str, str] = resolver(request.path)
    if props and props.get("$read"):
        data = await getattr(controller, props["$read"])(*props.get("$args"))
        if isinstance(data, Error):
            return data.get_response()
        response = [{"path": request.path, "data": data}]
    elif props and props.get("$watchable"):
        response = [{"path": request.path, "data": None}]
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
    response: Dict[str, Dict] = controller.i_schema.copy()
    response["wsurl"] = cfg.ws.url
    response["controller"] = controller.__class__.__name__
    return web.json_response(response)


async def get_index(request: web.Request) -> web.Response:
    return web.FileResponse(f"{bundle_dir}/webdist/index.html")


async def get_favicon(request: web.Request) -> web.Response:
    return web.FileResponse(f"{bundle_dir}/webdist/favicon.ico")


async def start_heartbeat(request: web.Request) -> web.Response:
    global WATCHING_PULSE
    if not WATCHING_PULSE:
        WATCHING_PULSE = True
        await controller.i_tend(spawn, request)
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
    app.router.add_static("/js", path=f"{bundle_dir}/webdist/js")
    app.router.add_static("/css", path=f"{bundle_dir}/webdist/css")
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

resolver: callable = makeresolver(controller.i_schema)
controller.i_setcallback(handleupdates)


if __name__ == "__main__":
    main()

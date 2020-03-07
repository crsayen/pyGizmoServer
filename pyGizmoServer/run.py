import sys
import time
import importlib
import json
from pyGizmoServer.utility import loadconfig, \
    makeresolver, debug, setuplog, ensurelist
from pyGizmoServer.subscription_server import SubscriptionServer
from aiohttp import web
from aiojobs.aiohttp import setup
from aiojobs.aiohttp import spawn
from typing import List, Dict, Tuple, Optional, Union


async def handlepatch(request: web.Request) -> web.Response:
    await controller.tend(spawn, request)
    patchlist: List[Dict[str, any]] = ensurelist(json.loads(await request.text()))
    debug(request)
    response: List = []
    for patch in patchlist:
        path, value = patch.get("path"), patch.get("value")
        props: Dict[str, str] = resolver(path)
        if not (
            props and value is not None and hasattr(controller, props.get("w"))
        ):
            return web.json_response([{"error": f"bad request: {patch}"}])
        getattr(controller, props["w"])(*(props["args"] + [value]))
        response.append({"path": path, "data": value})
    controller.finished_processing_request()
    return web.json_response(response)


async def handleget(request: web.Request) -> web.Response:
    debug(request.path)
    await controller.tend(spawn, request)
    props: Dict[str, str] = resolver(request.path)
    if props and props.get("r"):
        response = [{
            "path": request.path,
            "data": await getattr(controller, props["r"])(*props.get("args"))
        }]
    else:
        return web.json_response([{"error": f"bad request: {request}"}])
    return web.json_response(response)


def handleupdates(updates: Union[Dict[str, any], List[Dict[str, any]]]) -> None:
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


def make_app() -> web.Application:
    controller.start()
    app = web.Application()
    app["static_root_url"] = "/src"
    app.router.add_get("/", get_index)
    app.router.add_get("/FAVICON", get_favicon)
    app.router.add_static("/js", path="./dist/js")
    app.router.add_static("/css", path="./dist/css")
    app.router.add_route("GET", "/schema", get_schema)
    app.router.add_route("GET", r"/{tail:.*}", handleget)
    app.router.add_route("PATCH", r"/{tail:.*}", handlepatch)
    app.router.add_route("POST", r"/{tail:.*}", handlepatch)
    setup(app)
    return app


def main():
    try:
        print(time.asctime(), f"Server super started - {cfg.tcp.ip}:{cfg.tcp.port}")
        web.run_app(make_app(), host=cfg.tcp.ip, port=cfg.tcp.port, access_log=None)
    except KeyboardInterrupt:
        sys.exit()


configfile: str = sys.argv[1] if len(sys.argv) > 1 else "production"
cfg: Dict[str, any] = loadconfig(configfile)
setuplog(cfg)
if cfg is None:
    print(f"\n'{configfile}' not found\nexiting...\n")
    sys.exit()
subscription_server: SubscriptionServer = SubscriptionServer(cfg.ws.ip, cfg.ws.port)
controller = getattr(
    importlib.import_module(f"{cfg.controller}.{cfg.controller}"), cfg.controller
)()
resolver: callable = makeresolver(controller.schema)
controller.setcallback(handleupdates)


if __name__ == "__main__":
    main()

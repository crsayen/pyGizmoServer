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


async def handlepatch(request):
    await controller.tend(spawn, request)
    request = json.loads(await request.text())
    debug(request)
    response = []
    for r in ensurelist(request):
        path, value = r.get("path"), r.get("value")
        props = resolver(path)
        if not (
            props and value is not None and hasattr(controller, props.get("w"))
        ):
            return web.json_response([{"error": f"bad request: {r}"}])
        getattr(controller, props["w"])(*(props["args"] + [value]))
        response.append({"path": path, "data": value})
    controller.finished()
    return web.json_response(response)


async def handleget(request):
    debug(request.path)
    await controller.tend(spawn, request)
    props = resolver(request.path)
    if props and props.get("r"):
        response = await getattr(controller, props["r"])(*props.get("args"))
    else:
        return web.json_response([{"error": f"bad request: {request}"}])
    return web.json_response(response)


def handleupdates(updates):
    debug(updates)
    if not isinstance(updates, list):
        updates = [updates]
    for update in updates:
        data, path = update.get("data"), update.get("path")
        subscription_server.publish({"path": path, "value": data})


async def get_schema(request):
    debug(request.path)
    resp = controller.schema.copy()
    resp["wsurl"] = cfg.ws.url
    resp["controller"] = controller.__class__.__name__
    return web.json_response(resp)


async def get_index(request):
    return web.FileResponse("./dist/index.html")


async def get_favicon(request):
    return web.FileResponse("./dist/favicon.ico")


def make_app():
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


configfile = sys.argv[1] if len(sys.argv) > 1 else "production"
cfg = loadconfig(configfile)
setuplog(cfg)
if cfg is None:
    print(f"\n'{configfile}' not found\nexiting...\n")
    sys.exit()
subscription_server = SubscriptionServer(cfg.ws.ip, cfg.ws.port)
controller = getattr(
    importlib.import_module(f"{cfg.controller}.{cfg.controller}"), cfg.controller
)()
resolver = makeresolver(controller.schema)
controller.setcallback(handleupdates)


if __name__ == "__main__":
    main()

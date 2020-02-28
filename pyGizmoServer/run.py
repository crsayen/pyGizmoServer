import asyncio
import sys
import time
import importlib
import json
from pyGizmoServer.utility import Settings, makeresolver
from pyGizmoServer.subscription_server import SubscriptionServer
from aiohttp import web
from aiojobs.aiohttp import setup
from aiojobs.aiohttp import spawn


async def handlepatch(request):
    if not controller.running:
        await spawn(request, controller.usbrxhandler())
    request = json.loads(await request.text())
    if not isinstance(request, list):
        request = [request]
    response = []
    for r in request:
        path, value = r.get("path"), r.get("value")
        props = resolver(path)
        if not (
            props and value is not None and hasattr(controller, props.get("w"))
        ):
            return web.json_response([{"error": f"bad request: {r}"}])
        getattr(controller, props["w"])(*(props["args"] + [value]))
        response.append({"path": path, "data": value})
    controller.finished()
    """
    create and apply the requested PATCH to the model
    """
    return web.json_response(response)


async def handleget(request):
    if not controller.running:
        await spawn(request, controller.usbrxhandler())
    if request.path == "/schema":
        resp = controller.schema.copy()
        resp["wsurl"] = cfg.ws.url
        resp["controller"] = controller.__class__.__name__
        return web.json_response(resp)
    props = resolver(request.path)
    if props and props.get("r"):
        response = await getattr(controller, props["r"])(*props.get("args"))
    else:
        return web.json_response([{"error": f"bad request: {request}"}])
    return web.json_response(response)


def handleupdates(updates):
    if not isinstance(updates, list):
        updates = [updates]
    for update in updates:
        path, data = update.get("data"), update.get("path")
        subscription_server.publish({"path": path, "value": data})


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
cfg = Settings.load(configfile)
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

from pyGizmoServer.modification_handler import ModificationHandler
from pyGizmoServer.query_handler import QueryHandler
from controllers.testcube_usb_controller import TestCubeUSB
from controllers.mock_controller import MockUSB
from tests.mock_variables import MockVars
import sys, asyncio, sys, time, json, textwrap
from aiohttp import web
from aiojobs.aiohttp import setup, spawn, atomic
from yattag import Doc
from pyGizmoServer.render_index import *
import time, jinja2, aiohttp_jinja2, logging, aiojobs
import pkg_resources, os

version = pkg_resources.require("pyGizmoServer")[0].version

logger = logging.getLogger('gizmoLogger')
logger.setLevel(logging.INFO)
formatter = logging.Formatter(fmt='%(asctime)s.%(msecs)03d %(levelname)s {%(module)s} [%(funcName)s] %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S') 
handler = logging.FileHandler(filename='gizmo.log', mode='w')
handler.setFormatter(formatter)
logger.addHandler(handler)
starttime = time.strftime("%Y-%m-%d %H:%M")
logger.info(starttime)


coro_running = False

with open('schemas/testcube_HW.json') as f:
    hwschema = json.load(f)

tcp_ip, tcp_port = "0.0.0.0", 36364
ws_ip, ws_port = "0.0.0.0", 11111

model = MockVars().mock_model        
modification_handler = ModificationHandler(hwschema, model=model)
query_handler = QueryHandler(ws_ip, ws_port, hwschema, model=model)
controller = MockUSB(query_handler.handle_updates)

@aiohttp_jinja2.template('index.html')
async def get_index(request):
    return {'title': 'PyGizmoServer', 'version': version, 'time_started': starttime}

@atomic
async def start_your_engines(request):
    global coro_running
    if not coro_running:
        await spawn(request, controller.usbrxhandler())
        coro_running = True
    return web.Response(text="VROOM")

def make_app():
    print(os.getcwd())
    controller.start()
    modification_handler.add_controller(controller)
    query_handler.add_controller(controller)

    app = web.Application(loop=asyncio.get_event_loop())
    aiohttp_jinja2.setup(app,loader=jinja2.FileSystemLoader(['templates', 'static']))
    app['static_root_url'] = '/static'
    print(app['static_root_url'])
    app.router.add_get('/', get_index)
    app.router.add_static('/static', "static")
    app.router.add_get('/gizmogo', start_your_engines)
    app.router.add_route('GET', r'/{tail:.*}', query_handler.handle_get)
    app.router.add_route('PATCH', r'/{tail:.*}', modification_handler.handle_patch_from_client)
    setup(app)
    return app

def main():
    try:
        print(time.asctime(), f"Server started - {tcp_ip}:{tcp_port}")
        web.run_app(make_app(), host=tcp_ip, port=tcp_port)
    except KeyboardInterrupt:
        sys.exit()



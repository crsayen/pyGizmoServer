from http.server import HTTPServer
from socketserver import ThreadingMixIn
from pyGizmoServer.modification_handler import ModificationHandler
from pyGizmoServer.query_handler import QueryHandler
from controllers.testcube_usb_controller import TestCubeUSB
from controllers.mock_controller import MockUSB
from tests.mock_variables import MockVars
import sys, asyncio, sys
import time, json
import textwrap
from aiohttp import web
from aiojobs.aiohttp import setup, spawn
import aiojobs
import logging
from aiojobs.aiohttp import atomic

logger = logging.getLogger('gizmoLogger')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.FileHandler(filename='gizmo.log', mode='w'))

with open('schemas/testcube_HW.json') as f:
    hwschema = json.load(f)

tcp_ip, tcp_port = "0.0.0.0", 36364
ws_ip, ws_port = "0.0.0.0", 11111

model = MockVars().mock_model        
modification_handler = ModificationHandler(hwschema, model=model)
query_handler = QueryHandler(ws_ip, ws_port, hwschema, model=model)
controller = TestCubeUSB(query_handler.handle_updates)

@atomic
async def handler(request):
    await spawn(request, controller.usbrxhandler())
    return web.Response(text="this is a response I hope to receive")

def make_app():
    controller.start()
    modification_handler.add_controller(controller)
    query_handler.add_controller(controller)

    app = web.Application(loop=asyncio.get_event_loop())
    app.router.add_get('/', handler)
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



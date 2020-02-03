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

logging.basicConfig(filename='gizmo.log',level=logging.DEBUG)

with open('schemas/testcube_HW.json') as f:
    hwschema = json.load(f)

address = ('0.0.0.0', 36364)
model = MockVars().mock_model        
modification_handler = ModificationHandler(hwschema, model=model)
query_handler = QueryHandler(address, hwschema, model=model)
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
        print(time.asctime(), f"Server started - {address}")
        web.run_app(make_app(), host='localhost', port=36364)
    except KeyboardInterrupt:
        sys.exit()



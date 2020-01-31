import websockets, asyncio, time




connected = set()

async def handler(websocket, path):
    # Register.
    connected.add(websocket)
    print(path)
    try:
        # Implement logic here.
        await asyncio.wait([ws.send("Hello!") for ws in connected])
        await asyncio.sleep(10)
    finally:
        # Unregister.
        connected.remove(websocket)

server = websockets.serve(handler, "0.0.0.0", 11111)
asyncio.get_event_loop().run_until_complete(server)
asyncio.get_event_loop().run_forever()

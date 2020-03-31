import asyncio

async def get(init_cb, event, retry=0):
    print("in get")
    init_cb()
    if event is None:
        event = asyncio.Event()
    else:
        event.clear()
    try:
        await asyncio.wait_for(event.wait(), timeout=0.1)
    except:
        if retry < 5:
            return await get(init_cb, event,retry + 1)
        return False
    return True

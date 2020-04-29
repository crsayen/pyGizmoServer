import asyncio


async def get(init_cb, event, retry=0):
    event.clear()
    init_cb()
    try:
        await asyncio.wait_for(event.wait(), timeout=0.1)
    except:
        # if retry < 5:
        #     return await get(init_cb, event,retry + 1)
        return False
    return True

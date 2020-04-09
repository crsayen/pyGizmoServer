import asyncio
from pyGizmoServer.utility import Error, repeatOnFailAsync
from TestCubeUSB.getter import get

class RelayMessage:
    def __init__(self):
        self.getRelaysEvent = asyncio.Event()
        self.RelayStates = [None] * 6
        self.expectRelayMsg = False

    def resetRelayMessage(self):
        self.expectRelayMsg = None
        pass

    def setRelay(self, relay: int, state: bool):
        self.expectRelayMsg = True
        self.RelayStates[relay] = state

    async def getRelay(self, index):
        self.expectRelayMsg = True
        ret = await repeatOnFailAsync(5, self._getRelay, [index])
        if ret is not None:
            return ret
        return Error("Failed to read relay state")

    async def _getRelay(self, index):
        self.RelayStates = [''] * 6
        if await get(self.finished_processing_request, self.getRelaysEvent):
            return self.RelayStates[index]

    def get_relay_messages(self):
        if not self.expectRelayMsg:
            return []
        mask = 0
        val = 0
        for i in range(0, len(self.RelayStates)):
            if self.RelayStates[i] not in (None, ''):
                mask |= 1 << i
                if self.RelayStates[i]:
                    val |= 1 << i
        return [f"{0x12:08x}{mask:02x}{val:02x}"]

    def rec_usb_13_relay(self, payload):
        enabled = int(payload[:2], 16)
        data = [not not (enabled & (1 << x)) for x in range(6)]
        path = "/relayController/relays"
        self.RelayStates = data
        if not self.getRelaysEvent.is_set():
            self.getRelaysEvent.set()
        return [{"path": path, "data": self.RelayStates}]

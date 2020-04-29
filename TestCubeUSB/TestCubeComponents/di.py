import asyncio
from TestCubeUSB.getter import get
from pyGizmoServer.utility import Error, repeatOnFailAsync


class DiMessage:
    def __init__(self):
        self.getDiEvent = asyncio.Event()
        self.dimonitorrate = None
        self.dis = None

    def resetDiMessage(self):
        pass

    async def getDI(self, index):
        ret = await repeatOnFailAsync(5, self._getDI, [index])
        if ret is not None:
            return ret
        return Error("Failed to read actuator current")

    async def _getDI(self, index):
        if self.dimonitorrate:
            return self.dis[index]
        else:
            self.dimonitorrate = 0
            # self.finished_processing_request()
            if await get(self.finished_processing_request, self.getDiEvent):
                return self.dis[index]

    def setDiMonitorUpdateRate(self, rate: int):
        self.dimonitorrate = int(rate / 50)

    def get_di_messages(self):
        if self.dimonitorrate == None:
            return []
        return [f"{0xa:08x}{self.dimonitorrate:02x}"]

    def rec_usb_b_digitalinputs(self, payload):
        high = int(payload[:4], 16)
        self.dis = [not not (high & (1 << x)) for x in range(12)]
        if not self.getDiEvent.is_set():
            self.getDiEvent.set()
        return [{"path": "/digitalInputController/digitalInputs", "data": self.dis}]

import asyncio
from TestCubeUSB.getter import get
from pyGizmoServer.utility import Error, repeatOnFailAsync

class ActCurMessage:
    def __init__(self):
        self.lock = asyncio.Lock()
        self.actmonitorRate = None
        self.actmonitorChannels = 0x0FFF
        self.actmonitorThreshold = 60
        self.getFaultsEvent = asyncio.Event()
        self.getFaults = False
        self.getActCurrentEvent = asyncio.Event()
        self.actuatorCurrents = [None, None, None, None, None, None, None, None, None, None, None, None]

    def resetActCurMessage(self):
        self.actuatorCurrents = [None, None, None, None, None, None, None, None, None, None, None, None]

    def setPwmCurrentMonitorUpdateRate(self, rate: int):
        rate = int(rate / 50)
        self.actmonitorRate = rate

    def setPwmFaultThreshold(self, threshold: int):
        self.actmonitorThreshold = int(threshold / 50)

    def setPwmCurrentMonitorChannels(self, channelMask: int):
        self.actmonitorChannels = channelMask

    async def getFaultMonitor(self, index, retry=0):
        self.getFaults = True
        if await get(self.finished_processing_request,self.getFaultsEvent):
            return self.actFaults[index]

    def setEvent(self, event):
        if not event.is_set():
            event.set()

    async def getActuatorCurrent(self, index):
        ret = await repeatOnFailAsync(5, self._getActuatorCurrent, [index])
        if ret is not None:
            return ret
        return Error("Failed to read actuator current")

    async def _getActuatorCurrent(self, index):
        if self.actmonitorRate:
            ret = self.actuatorCurrents["data"][index]
        else:
            self.actmonitorRate = 0
            self.finished_processing_request()
            if await get(self.finished_processing_request,self.getActCurrentEvent):
                return self.actuatorCurrents[index]

    def get_actcur_messages(self):
        return [
            f"{0xc:08x}{self.actmonitorChannels:04x}{self.actmonitorRate:02x}{self.actmonitorThreshold:02x}"
        ] if self.actmonitorChannels is not None \
        and self.actmonitorRate is not None \
        and self.actmonitorThreshold is not None \
        else []

    def get_actuator_faults(self):
        return ["0000001c0000"]

    def rec_usb_1d_actfault(self, payload):
        _, faults = (int(payload[:1], 16), int(payload[1:4], 16))
        self.actFaults = [True if (faults & (1 << x)) else False for x in range(12)]
        if not self.getFaultsEvent.is_set():
            self.getFaultsEvent.set()
        return [{"path": "/pwmController/faultMonitors", "data": self.actFaults}]

    def parsePayload(self, start, end, payload, chunks, firstMessage=False, lastMessage=False):
        payload = payload + "0" * 16  # pad to avoid errors
        payloadChunks = [
            int(payload[:4], 16),
            int(payload[4:8], 16),
            int(payload[8:12], 16),
            int(payload[12:16], 16),
        ]
        chunks = [payloadChunks[i] for i in chunks]
        # this first msg defines which channels are in subsequent msgs
        if firstMessage:
            self.actcurrent_listinfirstmsg = [
                i for i in [11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
                if (payloadChunks[0] & (1 << (i)))
            ]
        thismsg = self.actcurrent_listinfirstmsg[start:end]
        if thismsg is not None:
            for ch, v in zip(thismsg, chunks):
                if isinstance(ch, int):
                    self.actuatorCurrents[ch] = v
            # if we dont expect any more data, return the message
            if self.actcurrent_listinfirstmsg[end:] is None or lastMessage:
                self.setEvent(self.getActCurrentEvent)
                return [{"path": "/pwmController/measuredCurrents", "data": self.actuatorCurrents}]

    def rec_usb_00d_actcurrent(self, payload):
        self.parsePayload(0, 3, payload, [3,2,1], firstMessage=True)

    def rec_usb_10d_actcurrent(self, payload):
        self.parsePayload(3, 7, payload, [0,1,2,3])

    def rec_usb_20d_actcurrent(self, payload):
        self.parsePayload(7, 11, payload, [0,1,2,3])

    def rec_usb_30d_actcurrent(self, payload):
        self.parsePayload(11, 12, payload, [0], lastMessage=True)
import asyncio
from TestCubeUSB.getter import get
from pyGizmoServer.utility import Error

class ActCurMessage:
    def __init__(self):
        self.actmonitorRate = None
        self.actmonitorChannels = 0x0FFF
        self.actmonitorThreshold = 60
        self.getFaultsEvent = asyncio.Event()
        self.getFaults = False
        self.getActCurrentEvent = asyncio.Event()
        self.ret = [None] * 12

    def resetActCurMessage(self):
        self.ret = [None] * 12

    def setPwmCurrentMonitorUpdateRate(self, rate: int):
        rate = int(rate / 50)
        self.actmonitorRate = rate

    def setPwmFaultThreshold(self, threshold: int):
        self.actmonitorThreshold = int(threshold / 50)

    def setPwmCurrentMonitorChannels(self, channelMask: int):
        self.actmonitorChannels = channelMask

    async def getFaultMonitors(self, retry=0):
        self.getFaults = True
        self.finished_processing_request()
        if self.getFaultsEvent is None:
            self.getFaultsEvent = asyncio.Event()
        else:
            self.getFaultsEvent.clear()
        try:
            await asyncio.wait_for(self.getFaultMonitors.wait(), timeout=0.1)
        except:
            if retry < 5:
                return await self.getFaultsEvent(retry = retry + 1)
            raise RuntimeError("getFaultMonitors not responding")
        return self.actFaults

    async def getFaultMonitor(self, index, retry=0):
        self.getFaults = True
        if await get(self.finished_processing_request,self.getFaultsEvent):
            return self.actFaults[index]
        print("fault ded")
        return "doohicky"

    def setEvent(self, event):
        if not event.is_set():
            event.set()

    async def getActuatorCurrent(self, index):
        async def tryGetActuatorCurrent(retry=0):
            if self.actmonitorRate:
                ret = self.ret["data"][index]
            else:
                self.actmonitorRate = 0
                if await get(self.finished_processing_request,self.getActCurrentEvent):
                    print(len(self.ret))
                    print(index)
                    print()
                    ret = self.ret[index]
            if ret is None:
                if retry > 4:
                    return Error("Failed to read actuator current")
                return await tryGetActuatorCurrent(retry + 1)
            return ret
        return await tryGetActuatorCurrent()

    def get_actcur_messages(self):
        if self.actmonitorChannels == None:
            return []
        if self.actmonitorRate == None:
            return []
        if self.actmonitorThreshold == None:
            return []
        return [
            f"{0xc:08x}{self.actmonitorChannels:04x}{self.actmonitorRate:02x}{self.actmonitorThreshold:02x}"
        ]

    def get_actuator_faults(self):
        if self.getFaults is True:
            self.getFaults = False
        return ["0000001c0000"]

    def rec_usb_1d_actfault(self, payload):
        _, faults = (int(payload[:1], 16), int(payload[1:4], 16))
        self.actFaults = [True if (faults & (1 << x)) else False for x in range(12)]
        if not self.getFaultsEvent.is_set():
            self.getFaultsEvent.set()
        return [{"path": "/pwmController/faultMonitors", "data": self.actFaults}]

    def rec_usb_00d_actcurrent(self, payload):
        ret = [None] * 12
        self.ret = ret
        payload = payload + "0" * 16  # pad to avoid errors
        channels, cc, cb, ca = (
            int(payload[:4], 16),
            int(payload[4:8], 16),
            int(payload[8:12], 16),
            int(payload[12:16], 16),
        )
        # this first msg defines which channels are in subsequent msgs
        self.actcurrent_listinfirstmsg = [
            i for i in [11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0] if (channels & (1 << (i)))
        ]
        thismsg = self.actcurrent_listinfirstmsg[0:3]
        if thismsg is None:
            return None
        for ch, v in zip(thismsg, [cc, cb, ca]):
            if isinstance(ch, int):
                ret[ch] = v
        path = "/pwmController/measuredCurrents"
        if self.actcurrent_listinfirstmsg[3:] is None:
            self.setEvent(self.getActCurrentEvent)
            return [{"path": path, "data": ret}]
        else:
            self.ret = ret

    def rec_usb_10d_actcurrent(self, payload):
        ret = self.ret
        if len(ret) < 12:
            ret = [None] * (12 - len(ret)) + ret
        payload = payload + "0" * 16  # pad to avoid errors
        cd, cc, cb, ca = (
            int(payload[:4], 16),
            int(payload[4:8], 16),
            int(payload[8:12], 16),
            int(payload[12:16], 16),
        )
        thismsg = self.actcurrent_listinfirstmsg[3:7]
        if thismsg is None:
            return None
        for ch, v in zip(thismsg, [cd, cc, cb, ca]):
            if isinstance(ch, int):
                ret[ch] = v
        path = "/pwmController/measuredCurrents"
        if self.actcurrent_listinfirstmsg[7:] is None:
            self.setEvent(self.getActCurrentEvent)
            return [{"path": path, "data": ret}]
        else:
            self.ret = ret

    def rec_usb_20d_actcurrent(self, payload):
        ret = self.ret
        if len(ret) < 12:
            ret = [None] * (12 - len(ret)) + ret
        payload = payload + "0" * 16  # pad to avoid errors
        cd, cc, cb, ca = (
            int(payload[:4], 16),
            int(payload[4:8], 16),
            int(payload[8:12], 16),
            int(payload[12:16], 16),
        )
        thismsg = self.actcurrent_listinfirstmsg[7:11]
        if thismsg is None:
            return None
        for ch, v in zip(thismsg, [cd, cc, cb, ca]):
            if isinstance(ch, int):
                ret[ch] = v
        path = "/pwmController/measuredCurrents"
        if self.actcurrent_listinfirstmsg[11:] is None:
            self.setEvent(self.getActCurrentEvent)
            return [{"path": path, "data": ret}]
        else:
            self.ret = ret

    def rec_usb_30d_actcurrent(self, payload):
        ret = self.ret
        if len(ret) < 12:
            ret = [None] * (12 - len(ret)) + ret
        ret = self.ret
        payload = payload + "0" * 16  # pad to avoid errors
        cd = int(payload[:4], 16)
        thismsg = self.actcurrent_listinfirstmsg[11:]
        if thismsg is None:
            return None
        for ch, v in zip(thismsg, [cd]):
            if isinstance(ch, int):
                ret[ch] = v
        path = "/pwmController/measuredCurrents"
        self.setEvent(self.getActCurrentEvent)
        return [{"path": path, "data": ret}]
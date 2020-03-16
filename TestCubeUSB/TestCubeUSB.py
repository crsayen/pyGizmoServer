import usb.core
import usb.util
import asyncio
from aioify import aioify
from pyGizmoServer.controller import Controller
from TestCubeUSB.TestCubeComponents.adc import AdcMessage
from TestCubeUSB.TestCubeComponents.pwm import PwmMessage
from TestCubeUSB.TestCubeComponents.relay import RelayMessage
from TestCubeUSB.TestCubeComponents.di import DiMessage
from TestCubeUSB.TestCubeComponents.actuators import ActCurMessage
from TestCubeUSB.TestCubeComponents.frequency import FrequencyMessage
from TestCubeUSB.TestCubeComponents.usb import UsbMessage
from TestCubeUSB.TestCubeComponents.can import CanDatabaseMessage
from TestCubeUSB.TestCubeComponents.version import VersionMessage
from pyGizmoServer.utility import debug


class TestCubeUSB(
    Controller,
    RelayMessage,
    PwmMessage,
    DiMessage,
    ActCurMessage,
    UsbMessage,
    FrequencyMessage,
    AdcMessage,
    CanDatabaseMessage,
    VersionMessage,
):
    def call_parent_inits(self):
        RelayMessage.__init__(self)
        PwmMessage.__init__(self)
        DiMessage.__init__(self)
        ActCurMessage.__init__(self)
        UsbMessage.__init__(self)
        FrequencyMessage.__init__(self)
        AdcMessage.__init__(self)
        VersionMessage.__init__(self)

    def __init__(self):
        debug("init")
        Controller.__init__(self)
        self.call_parent_inits()
        self.version = None
        self.ask = None
        self.getVersionEvent = None
        self.usbrxcount = 0
        self.usbidparsers = {
            "00000005": self.rec_usb_5_pwmfreq,
            "00000007": self.rec_usb_7_pwmdutycycle,
            "00000009": self.rec_usb_9_pwmenable,
            "0000000b": self.rec_usb_b_digitalinputs,
            "0000000d": self.rec_usb_00d_actcurrent,
            "0000010d": self.rec_usb_10d_actcurrent,
            "0000020d": self.rec_usb_20d_actcurrent,
            "0000030d": self.rec_usb_30d_actcurrent,
            "0000000f": self.rec_usb_00f_speed,
            "0000010f": self.rec_usb_10f_speed,
            "00000011": self.rec_usb_011_adc,
            "00000111": self.rec_usb_111_adc,
            "00000211": self.rec_usb_211_adc,
            "00000013": self.rec_usb_13_relay,
            "0000001d": self.rec_usb_1d_actfault,
            "00000051": self.rec_usb_51_version,
        }
        self.actcurrent_listinfirstmsg = [11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
        self.adc_listinfirstmsg = []

    def setup(self):
        self.dev = None
        devs = usb.core.find(idVendor=0x2B87, idProduct=0x0001, find_all=True)
        if devs is not None:
            for dev in devs:
                dev.write(2, "0000050")
                self.dev = dev
                d = str(dev).split("\n")
                devdict = {}
                for line in d:
                    if "DEVICE ID" in line:
                        s = line.split(" ")
                        devdict["deviceid"] = s[2]
                        devdict["bus"] = s[5] + "." + s[7]
                    elif ":" in line:
                        k, v = line.split(":")[0].strip(), line.split(":")[1].strip()
                        devdict[k] = v
                self.send("/usb/usbinfo", devdict)
                return
        raise ValueError("Device not found")

    def finished_processing_request(self):
        debug(f"finished")
        msgs = self.get_relay_messages()
        msgs += self.get_pwm_messages()
        msgs += self.get_di_messages()
        msgs += self.get_actcur_messages()
        msgs += self.get_sendusb_messages()
        msgs += self.get_freq_messages()
        msgs += self.get_adc_messages()
        msgs += self.get_version_messages()
        for msg in msgs:
            self.dev.write(2, msg)
        self.call_parent_inits()

    async def handler(self):
        if self.getVersionEvent is None:
            self.getVersionEvent = asyncio.Event()
        try:
            msg = self.dev.read(130, 24, 1)
        except usb.core.USBError:
            return
        msg = "".join([chr(x) for x in msg])
        self.usbrxcount += 1
        self.send( updates =
            [
                {"path": "/usb/rxMessage", "data": msg},
                {"path": "/usb/rxCount", "data": self.usbrxcount},
            ]
        )

        d = self.rec_usb(msg)
        if d is None:
            return
        if len(d) > 0:
            self.send(updates = d)

    async def heartbeat(self):
        if await self.getFirmwareVersion():
            return True
        return False

    def rec_usb(self, msg):
        _id, payload = msg[:8], msg[8:]
        try:
            f = self.usbidparsers.get(_id.lower())
            if f is None:
                return []
        except Exception:
            pass
        if f is None:
            return []
        result = f(payload)
        return result

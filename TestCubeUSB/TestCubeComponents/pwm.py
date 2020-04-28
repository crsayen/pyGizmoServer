from pyGizmoServer.utility import debug, Error, logError
import re
import os
from io import StringIO
from pandas import read_excel, read_csv

class Compiler:
    def __init__(self):
        self.lastDuty = 0
        self.lastFreq = 0
        self.ops = {
            'gtv': self.parseGtv,
            'slp': self.parseSlp,
            'jmp': self.parseJmp
        }

    def createAddEntryMessage(self, channel, flag, small=0, large=0):
        return '00000014{:02x}{:02x}{:02x}{:04x}'.format(channel,flag,small,large)

    def createDcEntryMessage(self, channel, duty):
        self.lastDuty = duty
        return [self.createAddEntryMessage(channel, 0, small=duty)]

    def createDcRampEntryMessages(self, channel, end, duration):
        ret = [
            self.createAddEntryMessage(channel, 1, small=self.lastDuty, large=duration),
            self.createAddEntryMessage(channel, 0, small=end, large=0)
        ]
        self.lastDuty = end
        return ret

    def createFreqEntryMessage(self, channel, frequency):
        self.lastFreq = frequency
        bank = 0 if channel < 7 else 1
        return [self.createAddEntryMessage(channel, 4, small=bank, large=frequency)]

    def createFreqRampEntryMessage(self, channel, end, duration):
        bank = 0 if channel < 7 else 1
        ret = [
            self.createAddEntryMessage(channel, 4, small=bank, large=self.lastFreq),
            self.createAddEntryMessage(channel, 5, small=bank, large=duration),
            self.createAddEntryMessage(channel, 4, small=bank, large=end)
        ]
        self.lastFreq = end
        return ret

    def createJumpEntryMessage(self, channel, index):
        return [self.createAddEntryMessage(channel, 2, index)]

    def parseGtv(self, channel, value):
        if value[-1] == '%':
            return self.createDcEntryMessage(channel, int(value[:-1]))
        else:
            return self.createFreqEntryMessage(channel, int(value[:-2]))

    def parseSlp(self, channel, value, duration):
        if value[-1] == '%':
            return self.createDcRampEntryMessages(
                channel, 
                int(value[:-1]), 
                int(duration[:-2])
            )
        else:
            return self.createFreqRampEntryMessage(
                channel, 
                int(value[:-2]), 
                int(duration[:-2])
            )

    def parseJmp(self, channel, value):
        return self.createJumpEntryMessage(channel, int(value))

    def fromCsvString(self, string):
        df = read_csv(StringIO(string))
        return self._compile(df)

    def fromCsvFile(self, file):
        df = read_csv(file)
        return self._compile(df)

    def fromExcelFile(self, file):
        df = read_excel(file)
        return self._compile(df)

    def _compile(self, df):
        channels = list(df.columns.values)
        mask = int(''.join(['1' if i in channels  else '0' for i in range(1,13)][::-1]), 2)
        msgs = []
        for channel in channels:
            self.lastDuty = 0
            self.lastFreq = 0
            try:
                for line in df[channel].tolist():
                    lineChunks = line.split(' ')
                    f = self.ops.get(lineChunks[0].lower())
                    if f is None:
                        raise RuntimeError(f'invalid operation: {lineChunks[0]}')
                    msgs += f(channel, *lineChunks[1:])
            except:
                return None
        
        return (mask, msgs)

class PwmMessage:
    def __init__(self):
        self.Freq = [None] * 2
        self.Hiconf = [None] * 12
        self.PwmEnabled = [None] * 12
        self.Duty = [None] * 12
        self.profileIndecies = [None] * 12
        self.pwmStartMessage = []
        self.pwmPauseMessage = []
        self.pwmStopMessage = []
        self.profileEntries = []
        self.suppToBeEnPwms = [None] * 12
        self.pwmProfileUpdatesMessage = []
        self.pwmFaults = [False] * 12
        self.expectPwmMsg = False
        self.compiler = Compiler()

    def resetPwmMessage(self):
        self.pwmStartMessage = []
        self.expectPwmMsg = False
        self.pwmPauseMessage = []
        self.pwmStopMessage = []
        self.profileEntries = []
        self.pwmProfileUpdatesMessage = []

    def setPwmFrequencyA(self, hz: int):
        self.expectPwmMsg = True
        self.Freq[0] = hz

    def setPwmFrequencyB(self, hz: int):
        self.expectPwmMsg = True
        self.Freq[1] = hz

    def sethiconf(self, idx: int, activehi: str):
        self.expectPwmMsg = True
        if activehi.upper() == "HIGH":
            activehi = True
        elif activehi.upper() == "LOW":
            activehi = False
        else:
            raise ValueError("active configuration must be either high or low")
        self.Hiconf[idx] = activehi

    def setPwmDutyCycle(self, idx: int, duty: int):
        self.expectPwmMsg = True
        self.Duty[idx] = duty

    def setPwmEnabled(self, idx: int, enabled: bool):
        self.expectPwmMsg = True
        self.suppToBeEnPwms[idx] = enabled
        self.PwmEnabled[idx] = enabled

    def getUsbMsg8(self):
        if self.PwmEnabled == [None] * 12 or not self.expectPwmMsg:
            return []
        mask = 0
        val = 0
        for i in range(0, len(self.PwmEnabled)):
            if self.PwmEnabled[i] != None:
                mask |= 1 << i
                if self.PwmEnabled[i]:
                    val |= 1 << i
        return [f"{8:08x}{mask:04x}{val:04x}"]

    def getUsbMsg6(self, bank: int):
        if self.Duty[bank * 6 : bank * 6 + 6] == ([None] * 6) or not self.expectPwmMsg:
            return []

        dutymask = 0
        for i in range(6):
            if self.Duty[i + bank * 6] != None:
                dutymask |= 1 << i
        r = f"{6:08x}{bank:02x}{dutymask:02x}"
        for i in reversed(range(6)):
            r += f"{self.Duty[i+bank*6] or 0:02x}"
        return [r]

    def getUsbMsg4(self):
        if (self.Freq == [None] * 2) and (self.Hiconf == [None] * 12) or not self.expectPwmMsg:
            return []
        freqmask = 0x0
        hilomask = 0x000
        hiloval = 0x000
        for i in range(0, len(self.Freq)):
            if self.Freq[i] != None:
                freqmask |= 8 >> i

        for i in range(0, len(self.Hiconf)):
            if self.Hiconf[i] != None:
                hilomask |= 1 << i
                if self.Hiconf[i]:
                    hiloval |= 1 << i

        try:
            assert freqmask <= 0xF
            assert hilomask <= 0xFFF
            assert hiloval <= 0xFFF
        except:
            raise ValueError("PwmMessageFieldOverflow")

        r = "{:08x}{:01x}{:03x}0{:03x}{:04x}{:04x}".format(
            0x04, freqmask, hilomask, hiloval, self.Freq[0] or 0, self.Freq[1] or 0
        )
        return [r]

    def get_pwm_messages(self):
        msgs = (
            self.getUsbMsg4()
            + self.getUsbMsg6(0)
            + self.getUsbMsg6(1)
            + self.getUsbMsg8()
            + self.pwmStartMessage
            + self.pwmStopMessage
            + self.pwmPauseMessage
            + self.profileEntries
            + self.pwmProfileUpdatesMessage
        )
        self.expectPwmMsg = False
        debug(msgs)
        return msgs

    def rec_usb_5_pwmfreq(self, payload):
        acthi, freqa, freqb = payload[:4], payload[4:8], payload[8:12]
        d = []
        path = "/pwmController/bankA/frequency"
        data = int(freqa, 16)
        d.append({"path": path, "data": data})
        path = "/pwmController/bankB/frequency"
        data = int(freqb, 16)
        d.append({"path": path, "data": data})
        path = "/pwmController/pwms"
        data = [
            {"activeConfiguration": "high"}
            if (int(acthi, 16) & (1 << x))
            else {"activeConfiguration": "low"}
            for x in range(12)
        ]
        d.append({"path": path, "data": data})
        return d

    def rec_usb_7_pwmdutycycle(self, payload):
        pass
        # self.dutyFromPayload(payload)
        # if payload[:2] == '01':
        #     path = "/pwmController/pwms"
        #     return [{"path": path, "data": [{"dutyCycle": dc} for dc in self.Duty]}]

    def rec_usb_9_pwmenable(self, payload):
        d = []
        enabled = int(payload[:4], 16)
        data = [
            {"enabled": True} if (enabled & (1 << x)) else {"enabled": False}
            for x in range(12)
        ]
        for i, en in enumerate(data):
            self.PwmEnabled[i] = en["enabled"]
            if self.suppToBeEnPwms[i] is None:
                continue
            self.pwmFaults[i] = self.suppToBeEnPwms[i] and not en["enabled"]
        self.send(f"/pwmController/faults", self.pwmFaults)
        path = "/pwmController/pwms"
        d.append({"path": path, "data": data})
        return d

    def profileFromExcelFile(self, path):
        mask, entries = self.compiler.fromExcelFile(path)
        self.profileEntries = entries

    def profileFromCsvFile(self, path):
        mask, entries = self.compiler.fromCsvFile(path)
        self.profileEntries = entries

    def profileFromCsvString(self, path):
        mask, entries = self.compiler.fromCsvString(path)
        self.profileEntries = entries

    def startPwmProfile(self, index):
        self.pwmStartMessage = ["00000016{:03x}".format(1 << index)]

    def pausePwmProfile(self, index):
        self.pwmPauseMessage = ["00000017{:03x}".format(1 << index)]

    def stopPwmProfile(self, index):
        self.pwmStopMessage = ["00000018{:03x}".format(1 << index)]

    def createProfileMessageFromMask(self, _id, mask):
        if len(mask) != 3:
            logError(f"invalid mask: {mask}")
            return []
        try:
            int(mask, 16)
        except ValueError:
            logError(f"invalid mask: {mask}")
            return []
        msg = ["000000{}{}".format(_id, mask)]
        debug(msg)
        return msg

    def startPwmProfiles(self, mask):
        self.pwmStartMessage = self.createProfileMessageFromMask("16", mask)

    def pausePwmProfiles(self, mask):
        self.pwmPauseMessage = self.createProfileMessageFromMask("17", mask)

    def stopPwmProfiles(self, mask):
        self.pwmStopMessage = self.createProfileMessageFromMask("18", mask)

    def enablePwmProfileUpdates(self, enabled):
        payload = '01' if enabled else '00'
        self.pwmProfileUpdatesMessage = [f'0000001A{payload}']

    ##############################################################################
    ''' Duty Cycle - PWM profile '''
    ##############################################################################

    def dutyFromPayload(self, payload, start, stop):
        chunks = (
            int(payload[:2], 16),
            int(payload[2:4], 16),
            int(payload[4:6], 16),
            int(payload[6:8], 16),
            int(payload[8:10], 16),
            int(payload[10:12], 16),
            int(payload[12:14], 16),
            int(payload[14:16], 16),
        )
        self.Duty[start:stop] = chunks[:1:-1]

    def sendIfAllDutyMsgsRcvd(self):
        debug(self.Duty)
        if all([1 if dc is not None  else 0 for dc in self.Duty]):
            out = self.Duty.copy()
            self.Duty = [None] * 12
            path = "/pwmController/profiles/dutyCycles"
            return [{"path": path, "data": out}]
        return []

    def rec_1b_pwmProfileDuty(self, payload):
        self.dutyFromPayload(payload, 0, 6)
        return self.sendIfAllDutyMsgsRcvd()

    def rec_11b_pwmProfileDuty(self, payload):
        self.dutyFromPayload(payload, 6, 12)
        return self.sendIfAllDutyMsgsRcvd()

    ##############################################################################
    ''' Index - PWM profile '''
    ##############################################################################

    def indexFromPayload(self, payload, start, end):
        chunks = (
            int(payload[:2], 16),
            int(payload[2:4], 16),
            int(payload[4:6], 16),
            int(payload[6:8], 16)
        )
        self.profileIndecies[start:end] = chunks

    def sendIfAllIndexMsgsRcvd(self):
        debug(self.profileIndecies)
        if all([1 if i is not None  else 0 for i in self.profileIndecies]):
            out = self.profileIndecies.copy()
            self.profileIndecies = [None] * 12
            path = "/pwmController/profiles/indecies"
            return [{"path": path, "data": out}]
        return []

    def rec_21b_pwmProfileIndex(self, payload):
        self.indexFromPayload(payload, 0, 4)
        return self.sendIfAllIndexMsgsRcvd()

    def rec_31b_pwmProfileIndex(self, payload):
        self.indexFromPayload(payload, 4, 8)
        return self.sendIfAllIndexMsgsRcvd()

    def rec_41b_pwmProfileIndex(self, payload):
        self.indexFromPayload(payload, 8, 12)
        return self.sendIfAllIndexMsgsRcvd()

    ##############################################################################
    ''' Frequency - PWM profile '''
    ##############################################################################

    def rec_51b_pwmProfileFrequency(self, payload):
        return [
            {
                "path": "/pwmController/profiles/frequencies",
                "data": [
                    int(payload[:2], 16),
                    int(payload[2:4], 16)
                ]
            }
        ]
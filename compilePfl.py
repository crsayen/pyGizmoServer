import pandas as pd

lastDuty = lastFreq = 0

df = pd.read_excel("C:\\\\dev\\Untitled spreadsheet.xlsx")

channels = list(df.columns.values)

mask = int("".join(["1" if i in channels else "0" for i in range(1, 13)][::-1]), 2)


def createAddEntryMessage(channel, flag, small=0, large=0):
    return "00000014{:02x}{:02x}{:02x}{:04x}".format(channel, flag, small, large)


def createDcEntryMessage(channel, duty):
    global lastDuty
    lastDuty = duty
    return [createAddEntryMessage(channel, 0, small=duty)]


def createDcRampEntryMessages(channel, start, end, duration):
    global lastDuty
    ret = [
        createAddEntryMessage(channel, 1, small=lastDuty, large=duration),
        createAddEntryMessage(channel, 0, small=end, large=0),
    ]
    lastDuty = end
    return ret


def createFreqEntryMessage(channel, frequency):
    global lastFreq
    lastFreq = frequency
    bank = 0 if channel < 7 else 1
    return [createAddEntryMessage(channel, 4, small=bank, large=frequency)]


def createFreqRampEntryMessage(channel, start, end, duration):
    global lastFreq
    bank = 0 if channel < 7 else 1
    ret = [
        createAddEntryMessage(channel, 4, small=bank, large=lastFreq),
        createAddEntryMessage(channel, 5, small=bank, large=duration),
        createAddEntryMessage(channel, 4, small=bank, large=end),
    ]
    lastFreq = end
    return ret


def createJumpEntryMessage(channel, index):
    return [createAddEntryMessage(channel, 2, index)]


def parseGtv(channel, value):
    if value[-1] == "%":
        return createDcEntryMessage(channel, int(value[:-1]))
    else:
        return createFreqEntryMessage(channel, int(value[:-2]))


def parseSlp(channel, value, duration):
    start = 0
    if value[-1] == "%":
        return createDcRampEntryMessages(
            channel, start, int(value[:-1]), int(duration[:-2])
        )
    else:
        return createFreqRampEntryMessage(
            channel, start, int(value[:-2]), int(duration[:-2])
        )


def parseJmp(channel, value):
    return createJumpEntryMessage(channel, int(value))


ops = {"gtv": parseGtv, "slp": parseSlp, "jmp": parseJmp}

msgs = []
for channel in channels:
    lastDuty = 0
    lastFreq = 0
    for line in df[channel].tolist():
        lineChunks = line.split(" ")
        f = ops.get(lineChunks[0].lower())
        if f is None:
            raise RuntimeError(f"invalid operation: {lineChunks[0]}")
        msgs += f(channel, *lineChunks[1:])

with open("profile1.pfl", "w") as o:
    for msg in msgs:
        o.write(msg)
        o.write("\n")

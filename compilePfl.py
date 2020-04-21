import pandas as pd

df = pd.read_excel('C:\\\\dev\\xl.xlsx')

channels = list(df.columns.values)

mask = int(''.join(['1' if i in channels  else '0' for i in range(1,13)][::-1]), 2)

def createAddEntryMessage(channel, flag, small=0, large=0):
    return '{:02x}{:02x}{:02x}{:04x}'.format(channel,flag,small,large)

def createDcEntryMessage(channel, duty):
    return [createAddEntryMessage(channel, 0, small=duty)]

def createDcRampEntryMessages(channel, start, end, duration):
    return [
        createAddEntryMessage(channel, 1, small=start, large=duration),
        createAddEntryMessage(channel, 0, small=end, large=0)
    ]

def createFreqEntryMessage(channel, frequency):
    bank = 0 if channel < 7 else 1
    return [createAddEntryMessage(channel, 4, small=bank, large=frequency)]

def createFreqRampEntryMessage(channel, start, end, duration):
    bank = 0 if channel < 7 else 1
    return [
        createAddEntryMessage(channel, 4, small=bank, large=start),
        createAddEntryMessage(channel, 5, small=bank, large=duration),
        createAddEntryMessage(channel, 4, small=bank, large=end)
    ]

def createJumpEntryMessage(channel, index):
    return [createAddEntryMessage(channel, 2, index)]

def parseGtv(channel, value):
    if value[-1] == '%':
        return createDcEntryMessage(channel, int(value[:-1]))
    else:
        return createFreqEntryMessage(channel, int(value[:-2]))

ops = {
    'gtv': parseGtv,
    'slp': parseSlp,
    'jmp': parseJmp
}

for channel in channels:
    for line in df[channel].tolist():
        lineChunks = line.split(' ')
        f = ops.get(lineChunks[0])
        if f is None:
            raise RuntimeError(f'invalid operation: {lineChunks[0]}')
        f(channel, *lineChunks[1:])
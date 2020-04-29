import json


class MockVars:
    def __init__(self):
        self.mock_model = {
            "version": "11.10.13",
            "adcInputController": {
                "adcInputMonitorRate": 0,
                "adcInputs": [
                    {"enabled": False},
                    {"enabled": False},
                    {"enabled": False},
                    {"enabled": False},
                    {"enabled": False},
                    {"enabled": False},
                    {"enabled": False},
                    {"enabled": False},
                ],
                "adcInputVoltages": [1, 2, 3, 4, 5, 6, 7, 8],
            },
            "frequencyInputController": {
                "frequencyInputs": [
                    {"measuredFrequency": 1},
                    {"measuredFrequency": 2},
                    {"measuredFrequency": 3},
                    {"measuredFrequency": 4},
                ]
            },
            "digitalInputController": {
                "digitalInputs": [
                    True,
                    False,
                    True,
                    False,
                    True,
                    False,
                    True,
                    False,
                    True,
                    False,
                    True,
                    False,
                ]
            },
            "relayController": {"relays": [True, False, False, False, True, False]},
            "pwmController": {
                "bankA": {"frequency": 0x1000},
                "bankB": {"frequency": 0xFFF},
                "pwms": [
                    {
                        "activeConfiguration": "high",
                        "dutyCycle": 1,
                        "enabled": True,
                        "currentMonitor": {"measuredCurrent": 1, "faulty": True},
                    },
                    {
                        "activeConfiguration": "low",
                        "dutyCycle": 2,
                        "enabled": False,
                        "currentMonitor": {"measuredCurrent": 2, "faulty": False},
                    },
                    {
                        "activeConfiguration": "high",
                        "dutyCycle": 3,
                        "enabled": True,
                        "currentMonitor": {"measuredCurrent": 3, "faulty": True},
                    },
                    {
                        "activeConfiguration": "low",
                        "dutyCycle": 4,
                        "enabled": False,
                        "currentMonitor": {"measuredCurrent": 4, "faulty": False},
                    },
                    {
                        "activeConfiguration": "high",
                        "dutyCycle": 5,
                        "enabled": True,
                        "currentMonitor": {"measuredCurrent": 5, "faulty": True},
                    },
                    {
                        "activeConfiguration": "low",
                        "dutyCycle": 6,
                        "enabled": False,
                        "currentMonitor": {"measuredCurrent": 6, "faulty": False},
                    },
                    {
                        "activeConfiguration": "high",
                        "dutyCycle": 7,
                        "enabled": True,
                        "currentMonitor": {"measuredCurrent": 7, "faulty": True},
                    },
                    {
                        "activeConfiguration": "low",
                        "dutyCycle": 8,
                        "enabled": False,
                        "currentMonitor": {"measuredCurrent": 8, "faulty": False},
                    },
                    {
                        "activeConfiguration": "high",
                        "dutyCycle": 9,
                        "enabled": True,
                        "currentMonitor": {"measuredCurrent": 9, "faulty": True},
                    },
                    {
                        "activeConfiguration": "low",
                        "dutyCycle": 10,
                        "enabled": False,
                        "currentMonitor": {"measuredCurrent": 10, "faulty": False},
                    },
                    {
                        "activeConfiguration": "high",
                        "dutyCycle": 11,
                        "enabled": True,
                        "currentMonitor": {"measuredCurrent": 11, "faulty": True},
                    },
                    {
                        "activeConfiguration": "low",
                        "dutyCycle": 12,
                        "enabled": False,
                        "currentMonitor": {"measuredCurrent": 12, "faulty": False},
                    },
                ],
            },
        }
        self.mock_schema = {
            "relayController": {
                "relays": {"$count": 6, "w": "setRelay", "args": [], "$type": "boolean"}
            },
            "pwmController": {
                "bankA": {
                    "frequency": {
                        "w": "setPwmFrequencyA",
                        "args": [],
                        "$type": "integer",
                    }
                },
                "bankB": {
                    "frequency": {
                        "w": "setPwmFrequencyB",
                        "args": [],
                        "$type": "integer",
                    }
                },
                "pwmCurrentMonitorUpdateRate": {
                    "w": "setPwmCurrentMonitorUpdateRate",
                    "args": [],
                    "$type": "integer",
                },
                "faultThreshold": {
                    "w": "setPwmFaultThreshold",
                    "args": [],
                    "$type": "integer",
                },
                "pwms": {
                    "$count": 12,
                    "activeConfiguration": {
                        "w": "sethiconf",
                        "args": [],
                        "$type": "string",
                    },
                    "dutyCycle": {
                        "w": "setPwmDutyCycle",
                        "args": [],
                        "$type": "integer",
                    },
                    "enabled": {"w": "setPwmEnabled", "args": [], "$type": "boolean"},
                    "profile": {},
                    "currentMonitor": {
                        "faultDelay": {
                            "w": "setPwmFaultDelay",
                            "args": [],
                            "$type": "integer",
                        },
                        "faulty": {"args": [], "$type": "boolean"},
                        "measuredCurrent": {"args": [], "$type": "integer"},
                        "enabled": {
                            "w": "setPwmCurrentMonitorEnabled",
                            "args": [],
                            "$type": "boolean",
                        },
                    },
                },
            },
            "adcInputController": {
                "adcInputMonitorRate": {
                    "w": "setAdcMonitorUpdateRate",
                    "args": [],
                    "$type": "integer",
                },
                "adcInputs": {
                    "$count": 8,
                    "enabled": {"w": "setAdcEnabled", "args": [], "$type": "boolean"},
                },
                "adcInputVoltages": {"$count": 8, "args": [], "$type": "integer"},
            },
            "digitalInputController": {
                "digitalInputMonitorRate": {
                    "w": "setDiMonitorUpdateRate",
                    "args": [],
                    "$type": "integer",
                },
                "digitalInputs": {"$count": 12, "args": [], "$type": "boolean"},
            },
            "frequencyInputController": {
                "frequencyMonitorRate": {
                    "w": "setFrequencyMonitorRate",
                    "$type": "integer",
                    "args": [],
                },
                "frequencyInputs": {
                    "$count": 4,
                    "measuredFrequency": {"args": [], "$type": "integer"},
                    "enabled": {
                        "w": "setFrequencyInputEnabled",
                        "args": [],
                        "$type": "boolean",
                    },
                },
            },
            "canDatabase": {"$type": "string"},
            "usb": {
                "txMessage": {"w": "sendrawusb", "args": [], "$type": "hex"},
                "rxMessage": {"$type": "hex"},
                "rxCount": {"$type": "integer"},
                "usbinfo": {"$type": "string"},
            },
            "version": {"r": "getFirmwareVersion", "args": [], "$type": "string"},
        }

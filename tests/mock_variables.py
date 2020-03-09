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
                "adcInputVoltages": [
                    1,
                    2,
                    3,
                    4,
                    5,
                    6,
                    7,
                    8
                ]
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
                    {"high": True},
                    {"high": False},
                    {"high": True},
                    {"high": False},
                    {"high": True},
                    {"high": False},
                    {"high": True},
                    {"high": False},
                    {"high": True},
                    {"high": False},
                    {"high": True},
                    {"high": False},
                ]
            },
            "relayController": {
                "relays": [
                    True,
                    False,
                    False,
                    False,
                    True,
                    False,
                ]
            },
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

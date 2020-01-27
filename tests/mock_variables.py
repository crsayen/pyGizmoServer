import json

class MockVars:
    def __init__(self):
        self.mock_model = {
            "frequencyInputController":{
                "frequencyInputs":[
                    {"measuredFrequency": 1},
                    {"measuredFrequency": 2},
                    {"measuredFrequency": 3},
                    {"measuredFrequency": 4}
                ]
            },
            "digitalInputController" : {
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
                "relays" : [
                    { "enabled": False },
                    { "enabled": False },
                    { "enabled": False },
                    { "enabled": False },
                    { "enabled": False },
                    { "enabled": False }
                ]
            },
            "pwmController": {
                "bankA": {
                    "frequency": 0x1000,
                },
                "bankB": {
                    "frequency": 0xFFF,
                },
                "pwms" : [
                    { "activeConfiguration": 'high',
                        "dutyCycle": 1,
                    "enabled": True,
                    "currentMonitor": {
                        "measuredCurrent": 1
                    }
                     },
                    { "activeConfiguration": 'low',
                     "dutyCycle": 2,
                    "enabled": False ,
                           "currentMonitor": {
                        "measuredCurrent": 2
                    }},
                    { "activeConfiguration": 'high',
                     "dutyCycle": 3,
                    "enabled": True ,
                           "currentMonitor": {
                        "measuredCurrent": 3
                    }},
                    { "activeConfiguration": 'low',
                     "dutyCycle": 4,
                    "enabled": False,
                           "currentMonitor": {
                        "measuredCurrent": 4
                    } },
                    { "activeConfiguration": 'high',
                     "dutyCycle": 5,
                    "enabled": True,
                           "currentMonitor": {
                        "measuredCurrent": 5
                    } },
                    { "activeConfiguration": 'low',
                     "dutyCycle": 6,
                    "enabled": False,
                           "currentMonitor": {
                        "measuredCurrent": 6
                    } },
                    { "activeConfiguration": 'high',
                     "dutyCycle": 7,
                    "enabled": True ,
                           "currentMonitor": {
                        "measuredCurrent": 7
                    }},
                    { "activeConfiguration": 'low',
                     "dutyCycle": 8,
                    "enabled": False,
                           "currentMonitor": {
                        "measuredCurrent": 8
                    } },
                    { "activeConfiguration": 'high',
                     "dutyCycle": 9,
                    "enabled": True,
                           "currentMonitor": {
                        "measuredCurrent": 9
                    } },
                    { "activeConfiguration": 'low',
                     "dutyCycle": 10,
                    "enabled": False,
                           "currentMonitor": {
                        "measuredCurrent": 10
                    } },
                    { "activeConfiguration": 'high',
                     "dutyCycle": 11,
                    "enabled": True,
                           "currentMonitor": {
                        "measuredCurrent": 11
                    } },
                    { "activeConfiguration": 'low',
                     "dutyCycle": 12,
                    "enabled": False,
                           "currentMonitor": {
                        "measuredCurrent": 12
                    } }
                ]
            }
        }
        #print('insideMockModel' + str(self.mock_model))
        with open("tests/mock_HW.json", "r") as f:
            self.mock_schema = json.load(f)
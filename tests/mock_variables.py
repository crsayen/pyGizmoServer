import json

class MockVars:
    def __init__(self):
        self.mock_model = {
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
                    "enabled": True },
                    { "activeConfiguration": 'low',
                     "dutyCycle": 2,
                    "enabled": False },
                    { "activeConfiguration": 'high',
                     "dutyCycle": 3,
                    "enabled": True },
                    { "activeConfiguration": 'low',
                     "dutyCycle": 4,
                    "enabled": False },
                    { "activeConfiguration": 'high',
                     "dutyCycle": 5,
                    "enabled": True },
                    { "activeConfiguration": 'low',
                     "dutyCycle": 6,
                    "enabled": False },
                    { "activeConfiguration": 'high',
                     "dutyCycle": 7,
                    "enabled": True },
                    { "activeConfiguration": 'low',
                     "dutyCycle": 8,
                    "enabled": False },
                    { "activeConfiguration": 'high',
                     "dutyCycle": 9,
                    "enabled": True },
                    { "activeConfiguration": 'low',
                     "dutyCycle": 10,
                    "enabled": False },
                    { "activeConfiguration": 'high',
                     "dutyCycle": 11,
                    "enabled": True },
                    { "activeConfiguration": 'low',
                     "dutyCycle": 12,
                    "enabled": False }
                ]
            }
        }
        #print('insideMockModel' + str(self.mock_model))
        with open("tests/mock_HW.json", "r") as f:
            self.mock_schema = json.load(f)
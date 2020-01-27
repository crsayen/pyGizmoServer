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
                        "dutyCycle": 0,
                    "enabled": False },
                    { "activeConfiguration": 'low',
                     "dutyCycle": 0,
                    "enabled": False },
                    { "activeConfiguration": 'high',
                     "dutyCycle": 0,
                    "enabled": False },
                    { "activeConfiguration": 'low',
                     "dutyCycle": 0,
                    "enabled": False },
                    { "activeConfiguration": 'high',
                     "dutyCycle": 0,
                    "enabled": False },
                    { "activeConfiguration": 'low',
                     "dutyCycle": 0,
                    "enabled": False },
                    { "activeConfiguration": 'high',
                     "dutyCycle": 0,
                    "enabled": False },
                    { "activeConfiguration": 'low',
                     "dutyCycle": 0,
                    "enabled": False },
                    { "activeConfiguration": 'high',
                     "dutyCycle": 0,
                    "enabled": False },
                    { "activeConfiguration": 'low',
                     "dutyCycle": 0,
                    "enabled": False },
                    { "activeConfiguration": 'high',
                     "dutyCycle": 0,
                    "enabled": False },
                    { "activeConfiguration": 'low',
                     "dutyCycle": 0,
                    "enabled": False }
                ]
            }
        }
        #print('insideMockModel' + str(self.mock_model))
        with open("tests/mock_HW.json", "r") as f:
            self.mock_schema = json.load(f)
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
                    "frequency": 0,
                },
                "bankB": {
                    "frequency": 0,
                },
                "pwms" : [
                    { "dutyCycle": 0,
                    "enabled": False },
                    { "dutyCycle": 0,
                    "enabled": False },
                    { "dutyCycle": 0,
                    "enabled": False },
                    { "dutyCycle": 0,
                    "enabled": False },
                    { "dutyCycle": 0,
                    "enabled": False },
                    { "dutyCycle": 0,
                    "enabled": False },
                    { "dutyCycle": 0,
                    "enabled": False },
                    { "dutyCycle": 0,
                    "enabled": False },
                    { "dutyCycle": 0,
                    "enabled": False },
                    { "dutyCycle": 0,
                    "enabled": False },
                    { "dutyCycle": 0,
                    "enabled": False },
                    { "dutyCycle": 0,
                    "enabled": False }
                ]
            }
        }

        with open("tests/mock_HW.json", "r") as f:
            self.mock_schema = json.load(f)
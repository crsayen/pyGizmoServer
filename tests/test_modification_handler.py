from pyGizmoServer.modification_handler import ModificationHandler
from controllers.mock_controller import MockUSB
from pubsub import pub

class TestModificationHandler:
    def test_instantiation(self):
        with open('schemas/testcube_HW.json') as f:
            self.schema = json.load(f)
        with open('mocks/model.json') as f:
            self.schema = json.load(f)
        self.controller = MockUSB()
        self.modification_handler = ModificationHandler(
            self.controller,
            self.schema,
            model=self.model
        )
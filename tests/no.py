from pyGizmoServer.modification_handler import ModificationHandler



class MockController():
    def start(self):
        pass

    def r1(self, index, data):
        pass
    
    def r2(self, index, data):
        pass
    
    def r3(self, index, data):
        pass

    def r4(self, index, data):
        pass

    def finished(self):
        pass

s={"a":{"b":{"c":{"r":"r1","w":"w1"}}},"1":{"2":{"3":{"r":"r3","w":"w4"}}}}
cont = MockController()
modhand = ModificationHandler(cont,s,s)

class TestModificationHandler:
    def test_handle_patch():
        self.req = [{"op":"replace","path":"a/b.c/","value":"False"},
            {"op":"replace","path":".1.2.3/","value":True}]
        self.res = [{"path": "/a/b/c", "data": "False"},
            {"path": "/1/2/3", "data": True}]
        modhand.handle_patch(self.req)
        assert(self.model == self.res)

class A:
    def __init__(self):
        self.foo = '123'

    def test(self, name, value):
        setattr(self, name, value)
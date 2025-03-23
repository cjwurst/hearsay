# TODO: Learn how this works, lmao

class ReadonlyClassProperty():
    def __init__(self, f):
        self.f = f
    def __get__(self, _, owner):
        return self.f(owner)

class ReadonlyStaticProperty():
    def __init__(self, f):
        self.f = f
    def __get__(self, _, __):
        return self.f()
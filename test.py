class Foo():
    def __init__(self, x):
        self.x = x

    def bar(self, j):
        return self.x + j

a = Foo(1)
b = Foo(2)

f = a.bar

print(f(4))
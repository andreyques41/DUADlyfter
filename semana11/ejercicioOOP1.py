import math

class Circle():
    def __init__(self, radius):
        self.radius = radius

    def get_area(self):
        return math.pi * self.radius**2

circle1 = Circle(5)
print(circle1.get_area())
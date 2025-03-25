from math import pi
from abc import ABC, abstractmethod

# Abstract base class for shapes
class Shape(ABC):
    perimeter: float = 0.0
    area: float = 0.0

    # Abstract method to calculate perimeter
    @abstractmethod
    def calculate_perimeter():
        pass

    # Abstract method to calculate area
    @abstractmethod
    def calculate_area():
        pass

# Circle class inheriting from Shape
class Circle(Shape):
    radius: float

    def __init__(self, radius: float):
        self.radius = radius  # Initialize radius

    def calculate_perimeter(self):
        self.perimeter = 2 * pi * self.radius  # Calculate perimeter of the circle

    def calculate_area(self):
        self.area = pi * self.radius ** 2  # Calculate area of the circle

# Square class inheriting from Shape
class Square(Shape):
    side: float

    def __init__(self, side: float):
        self.side = side  # Initialize side length

    def calculate_perimeter(self):
        self.perimeter = 4 * self.side  # Calculate perimeter of the square

    def calculate_area(self):
        self.area = self.side ** 2  # Calculate area of the square

# Rectangle class inheriting from Shape
class Rectangle(Shape):
    length: float
    width: float

    def __init__(self, length: float, width: float):
        self.length = length  # Initialize length
        self.width  = width   # Initialize width

    def calculate_perimeter(self):
        self.perimeter = (self.length * 2) + (self.width * 2)  # Calculate perimeter of the rectangle

    def calculate_area(self):
        self.area = self.length * self.width  # Calculate area of the rectangle

# Function to execute and demonstrate the functionality of the shapes
def execute():
    # Create and calculate properties of a square
    square = Square(2)
    square.calculate_area()
    square.calculate_perimeter()
    print(f'Square:\n Side = {square.side} \n Perimeter = {square.perimeter:.2f} \n Area = {square.area:.2f}')
    
    # Create and calculate properties of a circle
    circle = Circle(3)
    circle.calculate_area()
    circle.calculate_perimeter()
    print(f'Circle:\n Radius = {circle.radius} \n Perimeter = {circle.perimeter:.2f} \n Area = {circle.area:.2f}')
    
    # Create and calculate properties of a rectangle
    rectangle = Rectangle(3, 2)
    rectangle.calculate_area()
    rectangle.calculate_perimeter()
    print(f'Rectangle:\n Length = {rectangle.length} Width = {rectangle.width} \n Perimeter = {rectangle.perimeter:.2f} \n Area = {rectangle.area:.2f}')

# Entry point of the script
if __name__ == '__main__':
    execute()
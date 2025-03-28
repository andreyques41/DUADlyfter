from math import pi
from abc import ABC, abstractmethod

# Abstract base class for shapes
class Shape(ABC):
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
    def __init__(self, radius: float):
        self.radius = radius  # Initialize radius

    def calculate_perimeter(self):
        return 2 * pi * self.radius  # Calculate perimeter of the circle

    def calculate_area(self):
        return pi * self.radius ** 2  # Calculate area of the circle

# Square class inheriting from Shape
class Square(Shape):
    def __init__(self, side: float):
        self.side = side  # Initialize side length

    def calculate_perimeter(self):
        return 4 * self.side  # Calculate perimeter of the square

    def calculate_area(self):
        return self.side ** 2  # Calculate area of the square

# Rectangle class inheriting from Shape
class Rectangle(Shape):
    def __init__(self, length: float, width: float):
        self.length = length  # Initialize length
        self.width  = width   # Initialize width

    def calculate_perimeter(self):
        return (self.length * 2) + (self.width * 2)  # Calculate perimeter of the rectangle

    def calculate_area(self):
        return self.length * self.width  # Calculate area of the rectangle

# Function to execute and demonstrate the functionality of the shapes
def execute():
    # Create and calculate properties of a square
    square = Square(2)
    print(f'Square:\n Side = {square.side} \n Perimeter = {square.calculate_perimeter():.2f} \n Area = {square.calculate_area():.2f}')
    
    # Create and calculate properties of a circle
    circle = Circle(3)
    print(f'Circle:\n Radius = {circle.radius} \n Perimeter = {circle.calculate_perimeter():.2f} \n Area = {circle.calculate_area():.2f}')
    
    # Create and calculate properties of a rectangle
    rectangle = Rectangle(3, 2)
    print(f'Rectangle:\n Length = {rectangle.length} Width = {rectangle.width} \n Perimeter = {rectangle.calculate_perimeter():.2f} \n Area = {rectangle.calculate_area():.2f}')

# Entry point of the script
if __name__ == '__main__':
    execute()
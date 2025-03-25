from abc import ABC, abstractmethod

class Shape(ABC):
    perimeter: float = 0.0
    area: float = 0.0

    @abstractmethod
    def calculate_perimeter():
        pass

    @abstractmethod
    def calculate_area():
        pass

def execute():
    pass

if __name__ == '__main__':
    execute()
class Animal:
    # Base class representing a generic animal
    def comer(self):
        print("The animal eats")

class Mammal(Animal):
    # Represents mammals, inherits from Animal
    def eat(self):
        print("The mammal eats")

class Pet(Animal):
    # Represents pets, inherits from Animal
    def eat(self):
        print("The pet eats")

class Dog1(Mammal, Pet):
    # Dog1 inherits from both Mammal and Pet
    # Method resolution order (MRO) will prioritize Mammal's 'eat' method
    pass

class Dog2(Pet, Mammal):
    # Dog2 inherits from both Pet and Mammal
    # Method resolution order (MRO) will prioritize Pet's 'eat' method
    pass

# Entry point of the script
if __name__ == '__main__':
    # Creating an instance of Dog1 and calling the 'eat' method
    loki = Dog1()
    loki.eat()

    # Creating an instance of Dog2 and calling the 'eat' method
    another_loki = Dog2()
    another_loki.eat()
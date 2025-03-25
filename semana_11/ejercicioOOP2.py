class Bus():
    def __init__(self, max_passengers):
        self.max_passengers = max_passengers
        self.passengers = [] 

    def add_passenger(self, person):
        if len(self.passengers) < self.max_passengers:
            self.passengers.append(person)
            print(f"Person {person.name} has entered the bus")
        else:
            print(f"Person {person.name} was not able to enter the bus, because it has reached its full capacity!")

    def remove_passenger(self, person):
        if person in self.passengers:
            self.passengers.remove(person)
            print(f"Person {person.name} has left the bus")
        else:
            print(f"Person {person.name} was not in the bus")

class Person():
    def __init__(self, name):
        self.name = name

if __name__ == '__main__':
    person1 = Person('Andy')
    person2 = Person('Juan')
    person3 = Person('Raul')
    person4 = Person('Josue')

    bus1 = Bus(3)
    bus1.add_passenger(person1)
    bus1.add_passenger(person2)
    bus1.add_passenger(person3)
    bus1.add_passenger(person4)
    bus1.remove_passenger(person1)
    bus1.remove_passenger(person4)
    bus1.add_passenger(person4)
    bus1.add_passenger(person1)

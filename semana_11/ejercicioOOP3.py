class Head():
    def __init__(self):
        print('Head created!')

class Hand():
    def __init__(self):
        print('Hand created!')

class Feet():
    def __init__(self):
        print('Feet created!')

class Arm():
    def __init__(self, hand: Hand):
        self.hand = hand
        print('Arm created!')

class Leg():
    def __init__(self, feet: Feet):
        self.feet = feet
        print('Leg created!')

class Torso():
    def __init__(self, head: Head, right_arm: Arm, left_arm: Arm):
        self.head = head
        self.right_arm = right_arm
        self.left_arm = left_arm
        print('Torso created!')

class Human():
    def __init__(self, torso: Torso, right_leg: Leg, left_leg: Leg):
        self.torso = torso
        self.right_leg = right_leg
        self.left_leg = left_leg
        print('Human created!')

def create_human():
    head = Head()
    right_hand = Hand()
    left_hand = Hand()
    right_arm = Arm(right_hand)
    left_arm = Arm(left_hand)
    right_feet = Feet()
    left_feet = Feet()
    right_leg = Leg(right_feet)
    left_leg = Leg(left_feet)
    torso = Torso(head, right_arm, left_arm)
    andy = Human(torso, right_leg, left_leg)

if __name__ == '__main__':
    create_human()
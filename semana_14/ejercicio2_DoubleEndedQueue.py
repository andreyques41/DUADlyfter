# Queue:            HEAD    ->  Node A  ->   Node B ->  None     
#                                               <-  TAIL
# Node class represents an element in the linked structure
class Node:
    data: str
    next: "Node"

    def __init__(self, data, next=None):
        self.data = data
        self.next = next

# LinkedStructure serves as a base class for linked data structures
class LinkedStructure:
    # Initializes the structure with a head node
    def __init__(self, head: Node):
        self.head = head

    # Prints the elements of the structure
    def print_structure(self, msg):
        print(msg)
        current_node = self.head

        while current_node is not None:
            print(current_node.data)
            current_node = current_node.next

# Queue class implements a queue using a linked structure
class Queue(LinkedStructure):
    # Adds a new node to the end of the queue
    def enqueue(self, new_node: Node):
        current_node = self.head

        while current_node.next is not None:
            current_node = current_node.next

        current_node.next = new_node

    # Removes the front node from the queue
    def dequeue(self):
        if self.head:
            self.head = self.head.next

# Stack class implements a stack using a linked structure
class Stack(LinkedStructure):
    # Adds a new node to the top of the stack
    def push(self, new_node: Node):
        new_node.next = self.head
        self.head = new_node

    # Removes the top node from the stack
    def pop(self):
        if self.head:
            self.head = self.head.next

# Stack class implements a stack using a linked structure
class DoubleEndedQueue(LinkedStructure):
    # Initializes the structure with a tail node
    def __init__(self, head: Node):
        self.head = head
        self.tail = head

    # Adds a new node at the top
    def push_left(self, new_node: Node):
        new_node.next = self.head
        self.head = new_node

    # Removes the top node
    def pop_left(self):
        if self.head:
            self.head = self.head.next
            if not self.head:  # If the queue becomes empty
                self.tail = None

    # Adds a new node to the end
    def push_right(self, new_node: Node):
        if not self.head:  # If the queue is empty
            self.head = new_node
            self.tail = new_node
        else:
            current_node = self.head
            while current_node.next is not None:
                current_node = current_node.next
            current_node.next = new_node
            self.tail = new_node  # Update tail after appending

    # Removes the last node
    def pop_right(self):
        if self.head:
            if self.head == self.tail:  # If there's only one node
                self.head = None
                self.tail = None
            else:
                current_node = self.head
                while current_node.next is not self.tail:
                    current_node = current_node.next
                current_node.next = None
                self.tail = current_node  # Update tail to the new last node

# Create nodes and demonstrate 
first_node = Node("Node A")
second_node = Node("Node B")
third_node = Node("Node C")
forth_node = Node("Node D")
fifth_node = Node("Node E")

my_structure = DoubleEndedQueue(first_node)
my_structure.push_left(second_node)
my_structure.push_left(third_node)
my_structure.push_right(forth_node)
my_structure.push_right(fifth_node)

my_structure.print_structure('1. Initial structure:')
my_structure.pop_right()
my_structure.print_structure('2. Structure after pop_right:')
my_structure.pop_left()
my_structure.print_structure('3. Structure after pop_left:')
my_structure.pop_right()
my_structure.print_structure('4. Structure after pop_right:')
my_structure.push_right(fifth_node)
my_structure.print_structure('5. Structure after push_right:')
my_structure.pop_left()
my_structure.print_structure('6. Structure after pop_left:')
my_structure.pop_right()
my_structure.print_structure('7. Structure after pop_right:')
my_structure.pop_right()
my_structure.print_structure('8. Structure after pop_right:')

my_structure.pop_left()
my_structure.pop_right()
my_structure.print_structure('Final Structure:')

# my_structure.pop()
# my_structure.print_structure('Structure after pop:')
# my_structure.pop()
# my_structure.print_structure('Structure after pop:')
# my_structure.push(forth_node)
# my_structure.print_structure('Structure after push:')
# my_structure.push(third_node)
# my_structure.print_structure('Structure after push:')

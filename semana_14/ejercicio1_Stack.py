# Queue:            HEAD    ->  Node A  ->   Node B   ->  Node C   ->  NONE

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
    def __init__(self, head):
        self.head = head

    # Prints the elements of the structure
    def print_structure(self, msg):
        print(msg)
        if not self.head:  # Check if the queue is empty
            print('The structure is empty!')
            return

        # Traverse the queue and print each node's data
        current = self.head
        while current:
            print(current.data, end=' -> ')
            current = current.next
        print('None')

# Queue class implements a queue using a linked structure
class Queue(LinkedStructure):
    # Adds a new node to the end of the queue
    def enqueue(self, new_node):
        current_node = self.head

        while current_node.next is not None:
            current_node = current_node.next

        current_node.next = new_node

    # Removes the front node from the queue
    def dequeue(self):
        if self.head:  # Check if the queue is not empty
            self.head = self.head.next  # Update the head to the next node
        else:
            print('Not able to dequeue, the structure is empty!')

# Stack class implements a stack using a linked structure
class Stack(LinkedStructure):
    # Adds a new node to the top of the stack
    def push(self, new_node):
        new_node.next = self.head
        self.head = new_node

    # Removes the top node from the stack
    def pop(self):
        if self.head:  # Check if the queue is not empty
            self.head = self.head.next  # Update the head to the next node
        else:
            print('Not able to pop, the structure is empty!')

# Create nodes and demonstrate stack operations
first_node = Node("Node A")
second_node = Node("Node B")
third_node = Node("Node C")
forth_node = Node("Node D")

my_structure = Stack(first_node)
my_structure.push(second_node)
my_structure.push(third_node)
my_structure.push(forth_node)

my_structure.print_structure('Initial structure:')
my_structure.pop()
my_structure.print_structure('Structure after pop:')
my_structure.pop()
my_structure.print_structure('Structure after pop:')
my_structure.pop()
my_structure.print_structure('Structure after pop:')
my_structure.pop()
my_structure.pop()
my_structure.print_structure('Structure after pop:')
my_structure.push(forth_node)
my_structure.print_structure('Structure after push:')
my_structure.push(third_node)
my_structure.print_structure('Structure after push:')

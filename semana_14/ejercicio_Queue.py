# Node class represents an individual element in the queue
class Node:
    data: str  # Data stored in the node
    next: "Node"  # Reference to the next node in the queue

    def __init__(self, data, next=None):
        self.data = data  # Initialize the node with data
        self.next = next  # Initialize the next reference (default is None)


# Queue class represents the queue data structure
class Queue:
    head: Node  # Reference to the first node in the queue

    def __init__(self, head):
        self.head = head  # Initialize the queue with a head node

    # Method to print the current structure of the queue
    def print_structure(self):
        if not self.head:  # Check if the queue is empty
            print('The structure is empty!')
            return

        # Traverse the queue and print each node's data
        current = self.head
        while current:
            print(current.data, end=' -> ')
            current = current.next
        print('None')

    # Method to add a new node to the end of the queue
    def enqueue(self, new_node):
        current_node = self.head

        # Traverse to the last node
        while current_node.next is not None:
            current_node = current_node.next

        # Add the new node at the end
        current_node.next = new_node

    # Method to remove the first node from the queue
    def dequeue(self):
        if self.head:  # Check if the queue is not empty
            self.head = self.head.next  # Update the head to the next node
        else:
            print('Not able to dequeue, the structure is empty!')


# Example usage of the Queue class
first_node = Node("Hola")  # Create the first node
my_queue = Queue(first_node)  # Initialize the queue with the first node

# Add more nodes to the queue
second_node = Node("Mundo")
my_queue.enqueue(second_node)

third_node = Node("third")
my_queue.enqueue(third_node)

forth = Node("forth")
my_queue.enqueue(forth)

# Print the queue structure
my_queue.print_structure()

# Perform dequeue operations and print the queue after each operation
print("DEQUEUE")
my_queue.dequeue()
my_queue.print_structure()

print("DEQUEUE")
my_queue.dequeue()
my_queue.print_structure()

print("DEQUEUE")
my_queue.dequeue()
my_queue.print_structure()

print("DEQUEUE")
my_queue.dequeue()
my_queue.print_structure()

# Attempt to dequeue from an empty queue
print("DEQUEUE")
my_queue.dequeue()
my_queue.print_structure()

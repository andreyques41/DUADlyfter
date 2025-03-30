# Represents a single node in a binary tree, which contains data and references to two children.
class Node:
    data: str
    child1: "Node"
    child2: "Node"

    def __init__(self, data, child1=None, child2=None):
        self.data = data
        self.child1 = child1
        self.child2 = child2

# Represents a binary tree structure with a root node and methods to traverse and print the tree.
class BinaryTree:
    root: Node

    def __init__(self, root):
        self.root = root

    # Prints the structure of the binary tree using a recursive approach.
    # Each level of the tree is indented for clarity.
    def print_structure(self, node=None, level=0):
        if not self.root:  # Check if the queue is empty
            print('The structure is empty!')
            return
        
        if node is None:
            node = self.root
        print("  " * level + f"Level {level}: {node.data}")
        if node.child1:
            self.print_structure(node.child1, level + 1)
        if node.child2:
            self.print_structure(node.child2, level + 1)

# Create nodes and demonstrate the binary tree structure
first_node = Node("Node A")
second_node = Node("Node B")
third_node = Node("Node C")
forth_node = Node("Node D")
fifth_node = Node("Node E")
sixth_node = Node("Node F")
seventh_node = Node("Node G")
eighth_node = Node("Node H")
ninth_node = Node("Node I")

# Example usage:
tree = BinaryTree(first_node)
first_node.child1 = second_node
first_node.child2 = third_node
second_node.child1 = forth_node
second_node.child2 = fifth_node
third_node.child1 = sixth_node
third_node.child2 = seventh_node
forth_node.child1 = eighth_node
forth_node.child2 = ninth_node

# Print the structure of the binary tree
tree.print_structure()


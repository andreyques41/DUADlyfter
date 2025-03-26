# A decorator function that wraps another function to print all arguments passed to it
def decorator(func):
    def wrapper(*args):
        for arg in args:
            if not isinstance(arg, (int, float)): 
                raise ValueError(f'The variable "{arg}" is neither int or float')
            
        func(args)
    return wrapper

# A function decorated with the decorator to handle arguments
@decorator
def execute1(*args):
    pass  

# Another function decorated with the decorator to handle arguments
@decorator
def execute2(*args):
    pass  

if __name__ == '__main__':
    try:
        # Execute the main program and handle exceptions
        execute1(5, 'a', [2, 4, 's'])  
        execute2('s', ['s', 3], True, False) 
    except Exception as ex:
        # Print any exception that occurs during execution
        print(ex)
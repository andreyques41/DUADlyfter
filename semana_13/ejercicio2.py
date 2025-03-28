# A decorator function that wraps another function to print all arguments passed to it
def decorator(func):
    def wrapper(*args, **kwargs):
        for arg in args:
            if not isinstance(arg, (int, float)): 
                raise ValueError(f'The variable "{arg}" is neither int or float')
        for key, value in kwargs.items():
            if not isinstance(value, (int, float)): 
                raise ValueError(f'The value {value} from variable "{key}" is neither int or float')
        func(*args, **kwargs)
    return wrapper

# A function decorated with the decorator to handle arguments
@decorator
def execute1(*args, **kwargs):
    pass  

# Another function decorated with the decorator to handle arguments
@decorator
def execute2(*args, **kwargs):
    pass  

if __name__ == '__main__':
    try:
        # Execute the main program and handle exceptions
        execute1(5, 1, 1, variable1=2)  
        execute2('s', ['s', 3], True, False) 
    except Exception as ex:
        # Print any exception that occurs during execution
        print(ex)
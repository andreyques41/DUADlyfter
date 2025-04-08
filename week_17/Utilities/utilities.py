from typing import Any

# Validates if the given string is a valid positive number.
def validate_positive_number(value: str) -> float:
    try:
        number = float(value)
        if number < 0:
            raise ValueError(f"The provided value '{value}' is negative. Please enter a positive number.")
        return number
    except ValueError as ex:
        if "could not convert" in str(ex):
            raise ValueError(f"The provided value '{value}' is not a valid number. Please enter a numeric value.")
        raise

# Validates if the given string is non-empty.
def validate_non_empty_string(value: str) -> str:
    if not value or not value.strip():
        raise ValueError("The input is empty or contains only whitespace. Please provide a non-empty string.")
    return value

# A simple debug print function for debugging purposes.
def debug_print(variable: Any) -> None:
    print(f"[DEBUG]: Type: {type(variable)}, Value: {variable}")

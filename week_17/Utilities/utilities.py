# Validates if the given string is a valid number.
def validate_number(value: str) -> float:
    try:
        return float(value)
    except ValueError:
        raise ValueError(f"Invalid number: '{value}'")

# Validates if the given string is non-empty.
def validate_non_empty_string(value: str) -> str | None:
    if value is None:
        return None
    if not value.strip():
        raise ValueError("The string cannot be empty or just whitespace.")
    return value


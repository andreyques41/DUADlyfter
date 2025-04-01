import pytest
from exercises.semana6_ejercicio5 import count_letters

def test_count_letters_returns_number_of_uppercase_and_lowercase_with_small_string():
    # Arrange
    input_string = 'ComUnidaD LyfTer'
    uppercase = 5
    lowercase = 10
    # Act
    result_upper, result_lower = count_letters(input_string)
    # Assert
    assert result_upper == uppercase and result_lower == lowercase, f"Expected {uppercase} uppercase and {lowercase} lowercase, but got {result_upper} uppercase and {result_lower} lowercase"

def test_count_letters_returns_number_of_uppercase_and_lowercase_with_all_upper_string():
    # Arrange
    input_string = 'COMUNIDAD LYFTER'
    uppercase = 15
    lowercase = 0
    # Act
    result_upper, result_lower = count_letters(input_string)
    # Assert
    assert result_upper == uppercase and result_lower == lowercase, f"Expected {uppercase} uppercase and {lowercase} lowercase, but got {result_upper} uppercase and {result_lower} lowercase"

def test_count_letters_throws_exception_with_invalid_string():
    # Arrange
    input_string = 2
    # Act & Assert
    with pytest.raises(ValueError, match="The input must be a string"):
        result_upper, result_lower = count_letters(input_string)
import pytest
from ejercicios.semana6_ejercicio7 import get_prime_numbers
from ejercicios.semana6_ejercicio7 import is_prime

def test_get_prime_numbers_returns_list_with_valid_list_of_numbers():
    # Arrange
    input_string = [13, 17, 23, 55, 88]
    prime_list = [13, 17, 23]
    # Act
    result_list = get_prime_numbers(input_string)
    # Assert
    assert result_list == prime_list, f"Expected {prime_list}, but got {result_list}"

def test_get_prime_numbers_returns_list_with_valid_list_of_no_primenumbers():
    # Arrange
    input_string = [4, 6, 10, 15, 80]
    prime_list = []
    # Act
    result_list = get_prime_numbers(input_string)
    # Assert
    assert result_list == prime_list, f"Expected {prime_list}, but got {result_list}"

def test_get_prime_numbers_throws_exception_with_invalid_input():
    # Arrange
    input_string = 2
    # Act & Assert
    with pytest.raises(ValueError, match="The input must be a list of numbers"):
        result_list = get_prime_numbers(input_string)

def test_is_prime_returns_true_with_prime_number():
    # Arrange
    input_number = 17
    # Act & Assert
    assert is_prime(input_number)

def test_is_prime_returns_false_with_no_prime_number():
    # Arrange
    input_number = 20
    # Act & Assert
    assert not is_prime(input_number)

def test_is_prime_throws_exception_with_invalid_input():
    # Arrange
    input_number = 's'
    # Act & Assert
    with pytest.raises(ValueError, match="The input must be a numeric value"):
        is_prime(input_number)
import pytest
from exercises.semana6_ejercicio3 import sum_from_list

def test_sum_from_list_returns_sum_with_valid_list():
    # Arrange
    input_list = [ 2, -6, 87, 0, -879, 89, 10]
    sum = -697
    # Act
    result_list = sum_from_list(input_list)
    # Assert
    assert result_list == sum

def test_sum_from_list_throws_exception_with_empty_list():
    # Arrange
    input_list = []
    # Act & Assert
    with pytest.raises(ValueError, match="Input list cannot be empty"):
        result_list = sum_from_list(input_list)

def test_sum_from_list_throws_exception_with_invalid_list():
    # Arrange
    input_list = 's'
    # Act & Assert
    with pytest.raises(ValueError, match="The input must be a list of numbers"):
        result_list = sum_from_list(input_list)
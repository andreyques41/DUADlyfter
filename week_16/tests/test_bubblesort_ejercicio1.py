import pytest
import random
from exercises.bubblesort_ejercicio1 import bubble_sort

def test_bubble_sort_returns_sorted_list_with_small_list():
    # Arrange
    input_list = [ 2, -6, 87, 0, -879, 89, 10]
    sorted_list = [ -879, -6, 0, 2, 10, 87, 89]
    # Act
    result_list = bubble_sort(input_list)
    # Assert
    assert result_list == sorted_list

def test_bubble_sort_returns_sorted_list_with_big_list():
    # Arrange
    random.seed(42)  # Set a fixed seed for reproducibility
    input_list = [random.randint(-1000, 1000) for _ in range(100)]
    sorted_list = sorted(input_list)
    # Act
    result_list = bubble_sort(input_list)
    # Assert
    assert result_list == sorted_list

def test_bubble_sort_throws_exception_list_with_empty_list():
    # Arrange
    input_list = []
    # Act & Assert
    with pytest.raises(ValueError, match="Input list cannot be empty"):
        result_list = bubble_sort(input_list)

def test_bubble_sort_throws_exception_with_invalid_input():
    # Arrange
    input_list = 's'
    # Act & Assert
    with pytest.raises(ValueError, match="The input must be a list of numbers"):
        result_list = bubble_sort(input_list)



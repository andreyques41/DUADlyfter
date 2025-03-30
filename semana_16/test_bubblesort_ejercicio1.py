import pytest
from bubblesort_ejercicio1 import bubble_sort

def test_bubble_sort_returns_sorted_list_with_small_list():
    # Arrange
    input_list = [ 2, -6, 87, 0, -879, 89, 10]
    sorted_list = [ -879, -6, 0, 2, 10, 87, 89]
    # Act
    bubble_sort(input_list)
    # Assert
    assert input_list == sorted_list

def test_bubble_sort_returns_sorted_list_with_big_list():
    # Arrange
    input_list = [ 2, -6, 87, 0, -879, 89, 10]
    sorted_list = [ -879, -6, 0, 2, 10, 87, 89]
    # Act
    bubble_sort(input_list)
    # Assert
    assert input_list == sorted_list

def test_bubble_sort_returns_sorted_list_with_empty_list():
    
    pass

def test_bubble_sort_returns_sorted_list_with_invalid_input():
    pass



import pytest
from ejercicios.semana6_ejercicio6 import sort_string1
from ejercicios.semana6_ejercicio6 import sort_string2
2
def test_sort_string1_returns_sorted_string_with_dash_separated_string():
    # Arrange
    input_string = 'hola-soy-un-unit-test'
    sorted_string = 'hola-soy-test-un-unit'
    # Act
    result_string = sort_string1(input_string)
    # Assert
    assert result_string == sorted_string, f"Expected {sorted_string}, but got {result_string}"

def test_sort_string1_returns_sorted_string_with_dot_separated_string():
    # Arrange
    input_string = 'hola.soy.un.unit.test'
    sorted_string = 'hola.soy.un.unit.test'
    # Act
    result_string = sort_string1(input_string)
    # Assert
    assert result_string == sorted_string, f"Expected {sorted_string}, but got {result_string}"

def test_sort_string1_returns_sorted_string_with_invalid_string():
    # Arrange
    input_string = 2
    # Act & Assert
    with pytest.raises(ValueError, match="The input must be a string"):
        result_string = sort_string1(input_string)

def test_sort_string2_returns_sorted_string_with_dash_separated_string():
    # Arrange
    input_string = 'hola-soy-un-unit-test'
    sorted_string = 'hola-soy-test-un-unit'
    # Act
    result_string = sort_string2(input_string)
    # Assert
    assert result_string == sorted_string, f"Expected {sorted_string}, but got {result_string}"

def test_sort_string2_returns_sorted_string_with_dot_separated_string():
    # Arrange
    input_string = 'hola.soy.un.unit.test'
    sorted_string = 'hola.soy.un.unit.test'
    # Act
    result_string = sort_string2(input_string)
    # Assert
    assert result_string == sorted_string, f"Expected {sorted_string}, but got {result_string}"

def test_sort_string2_throws_exception_with_invalid_string():
    # Arrange
    input_string = 2
    # Act & Assert
    with pytest.raises(ValueError, match="The input must be a string"):
        result_string = sort_string2(input_string)
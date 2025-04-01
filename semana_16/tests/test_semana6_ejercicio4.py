import pytest
from ejercicios.semana6_ejercicio4 import reverse_string
from ejercicios.semana6_ejercicio4 import reverse_string2
from ejercicios.semana6_ejercicio4 import reverse_string3

def test_reverse_string_returns_string_with_valid_string():
    # Arrange
    input_string = 'Lyfter'
    reversed_string = 'retfyL'
    # Act
    result_string = reverse_string(input_string)
    # Assert
    assert result_string == reversed_string

def test_reverse_string_throws_exception_with_empty_string():
    # Arrange
    input_string = ""
    # Act & Assert
    with pytest.raises(ValueError, match="The input string is empty"):
        result_string = reverse_string(input_string)

def test_reverse_string_throws_exception_with_invalid_string():
    # Arrange
    input_string = 2
    # Act & Assert
    with pytest.raises(ValueError, match="The input must be a string"):
        result_string = reverse_string(input_string)

def test_reverse_string2_returns_string_with_valid_string():
    # Arrange
    input_string = 'Lyfter'
    reversed_string = 'retfyL'
    # Act
    result_string = reverse_string2(input_string)
    # Assert
    assert result_string == reversed_string

def test_reverse_string2_throws_exception_with_empty_string():
    # Arrange
    input_string = ""
    # Act & Assert
    with pytest.raises(ValueError, match="The input string is empty"):
        result_string = reverse_string2(input_string)

def test_reverse_string2_throws_exception_with_invalid_string():
    # Arrange
    input_string = 2
    # Act & Assert
    with pytest.raises(ValueError, match="The input must be a string"):
        result_string = reverse_string2(input_string)

def test_reverse_string3_returns_string_with_valid_string():
    # Arrange
    input_string = 'Lyfter'
    reversed_string = 'retfyL'
    # Act
    result_string = reverse_string3(input_string)
    # Assert
    assert result_string == reversed_string

def test_reverse_string3_throws_exception_with_empty_string():
    # Arrange
    input_string = ""
    # Act & Assert
    with pytest.raises(ValueError, match="The input string is empty"):
        result_string = reverse_string3(input_string)

def test_reverse_string3_throws_exception_with_invalid_string():
    # Arrange
    input_string = 2
    # Act & Assert
    with pytest.raises(ValueError, match="The input must be a string"):
        result_string = reverse_string3(input_string)
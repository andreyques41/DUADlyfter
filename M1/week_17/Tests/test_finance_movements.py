import pytest
from Clases.finance_movements import Movement, FinanceMonth

# Test the creation of a Movement object and verify its attributes
def test_movement_creation():
    movement = Movement(name="Salary", category="Job", movement_type="Income", amount=5000)
    assert movement.name == "Salary"
    assert movement.category == "Job"
    assert movement.movement_type == "Income"
    assert movement.amount == 5000

# Test that an invalid movement type raises a ValueError
def test_movement_invalid_type():
    with pytest.raises(ValueError, match="Invalid movement type"):
        Movement(name="Invalid", category="Test", movement_type="InvalidType", amount=100)

# Test that a negative amount raises a ValueError
def test_movement_negative_amount():
    with pytest.raises(ValueError, match="Amount must be a positive number"):
        Movement(name="Negative", category="Test", movement_type="Expense", amount=-100)

import pytest
from Actions.finance_movements import Movement, FinanceMonth

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

# Test the calculation of totals (Income, Expense, Net) in a FinanceMonth object
def test_finance_month_calculate_totals():
    finance_month = FinanceMonth(month=1, year=2025)
    finance_month.add_movement(Movement(name="Salary", category="Job", movement_type="Income", amount=5000))
    finance_month.add_movement(Movement(name="Rent", category="Housing", movement_type="Expense", amount=1500))
    totals = finance_month.calculate_totals()
    assert totals['Income'] == 5000
    assert totals['Expense'] == 1500
    assert totals['Net'] == 3500
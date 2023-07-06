import pytest
import pendulum
from expenses_opt.models.expense import (
    Expense,
    ExpenseRange,
    build_expenses_from_csv,
)
from expenses_opt.constants import Priority

item_name = "Item 01"
date = pendulum.date(2023, 7, 31)


def test_add_partial_expense():
    my_range = ExpenseRange(100, 200, 150)
    my_expense = Expense(item_name, date, Priority.LOW, my_range)

    assert my_expense.cost == 0
    my_expense.add_partial_spend(50)
    assert my_expense.cost == 50


def test_add_big_spent_raises_error():
    my_range = ExpenseRange(100, 200, 150)
    my_expense = Expense(item_name, date, Priority.LOW, my_range)

    with pytest.raises(ValueError, match="Maximum spend achived for expense Item 01"):
        my_expense.add_partial_spend(300)


def test_add_big_partial_spents_raises_error():
    my_range = ExpenseRange(100, 200, 150)
    my_expense = Expense(item_name, date, Priority.LOW, my_range)

    my_expense.add_partial_spend(100)
    my_expense.add_partial_spend(90)
    my_expense.add_partial_spend(10)

    with pytest.raises(ValueError, match="Maximum spend achived for expense Item 01"):
        my_expense.add_partial_spend(1)


def test_build_expenses_from_csv():
    expenses = build_expenses_from_csv("csv_test.csv")
    assert len(expenses) == 11

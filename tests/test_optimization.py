import pytest
import pendulum
from expenses_opt.constants import Priority
from expenses_opt.models.portfolio import Portfolio, Budget
from expenses_opt.models.expense import Expense, ExpenseRange
from expenses_opt.optimization.builder import OptmizationParameters
from expenses_opt.optimization.optimizer import Optimizer
from expenses_opt.exceptions import InfeasibleProblemException
from expenses_opt.optimization.run import run_optimization_from_json

item01 = "Item 01"


def test_update_single_expense_cost():
    expense = Expense(
        description=item01,
        due_date=pendulum.date(2023, 1, 31),
        priority=Priority.LOW,
        range=ExpenseRange(900, 1200, 1000),
    )
    budget = Budget(
        initial=1000, recorrent=1000, recurrence=30, last_recurrence=0, iterations=1
    )
    portfolio = Portfolio(expenses=[expense], budget=budget)

    params = OptmizationParameters(
        priority_exponent=2, deviation_weight=0, max_time=1000
    )

    optimizer = Optimizer(
        portfolio=portfolio, parameters=params, start_date=pendulum.date(2023, 1, 1)
    )

    assert expense.cost == 0
    assert len(expense.partial_spends) == 0

    optimizer.solve_optimization_problem()

    assert expense.cost == 1000
    assert len(expense.partial_spends) == 1


def test_optimizer_chooses_high_priority_expense():
    expense_high = Expense(
        description="High expense",
        due_date=pendulum.date(2023, 1, 31),
        priority=Priority.HIGHT,
        range=ExpenseRange(900, 1200, 1000),
    )

    expense_medium = Expense(
        description="Medium expense",
        due_date=pendulum.date(2023, 1, 31),
        priority=Priority.MEDIUM,
        range=ExpenseRange(200, 900, 800),
    )

    expense_low = Expense(
        description="Low expense",
        due_date=pendulum.date(2023, 1, 31),
        priority=Priority.LOW,
        range=ExpenseRange(100, 500, 150),
    )

    budget = Budget(
        initial=1000, recorrent=1000, recurrence=30, last_recurrence=0, iterations=1
    )
    portfolio = Portfolio(
        expenses=[expense_low, expense_medium, expense_high], budget=budget
    )

    params = OptmizationParameters(
        priority_exponent=2, deviation_weight=0, max_time=1000
    )

    optimizer = Optimizer(
        portfolio=portfolio, parameters=params, start_date=pendulum.date(2023, 1, 1)
    )

    for expense in portfolio.expenses:
        assert expense.cost == 0

    optimizer.solve_optimization_problem()

    assert expense_high.cost == pytest.approx(1000)
    assert expense_medium.cost == pytest.approx(0)
    assert expense_low.cost == pytest.approx(0)


def test_optimizer_chooses_mandatory_expense():
    mandatory_expense = Expense(
        description="Mandatory expense",
        due_date=pendulum.date(2023, 1, 31),
        priority=Priority.LOW,
        range=ExpenseRange(1000, 1000, 1000),
        mandatory=True,
    )

    expense_medium = Expense(
        description="Medium expense",
        due_date=pendulum.date(2023, 1, 31),
        priority=Priority.MEDIUM,
        range=ExpenseRange(800, 800, 800),
    )

    expense_hight = Expense(
        description="High expense",
        due_date=pendulum.date(2023, 1, 31),
        priority=Priority.HIGHT,
        range=ExpenseRange(150, 150, 150),
    )

    budget = Budget(
        initial=1000, recorrent=1000, recurrence=30, last_recurrence=0, iterations=1
    )
    portfolio = Portfolio(
        expenses=[mandatory_expense, expense_medium, expense_hight], budget=budget
    )

    params = OptmizationParameters(
        priority_exponent=2, deviation_weight=0, max_time=1000
    )

    optimizer = Optimizer(
        portfolio=portfolio, parameters=params, start_date=pendulum.date(2023, 1, 1)
    )

    for expense in portfolio.expenses:
        assert expense.cost == 0

    optimizer.solve_optimization_problem()

    assert mandatory_expense.cost == pytest.approx(1000)
    assert expense_medium.cost == pytest.approx(0)
    assert expense_hight.cost == pytest.approx(0)


def test_do_not_spend_after_expense_due_date():
    expense1 = Expense(
        description=item01,
        due_date=pendulum.date(2023, 1, 31),
        priority=Priority.HIGHT,
        range=ExpenseRange(1000, 1000, 1000),
        mandatory=True,
    )

    expense2 = Expense(
        description="Item 02",
        due_date=pendulum.date(2023, 2, 25),
        priority=Priority.HIGHT,
        range=ExpenseRange(500, 500, 500),
        mandatory=True,
    )

    budget = Budget(
        initial=500, recorrent=1000, recurrence=30, last_recurrence=0, iterations=2
    )

    portfolio = Portfolio(expenses=[expense1, expense2], budget=budget)

    params = OptmizationParameters(
        priority_exponent=2, deviation_weight=0, max_time=1000
    )

    optimizer = Optimizer(
        portfolio=portfolio, parameters=params, start_date=pendulum.date(2023, 1, 1)
    )

    optimizer.solve_optimization_problem()

    assert expense1.cost == pytest.approx(1000)
    assert expense2.cost == pytest.approx(500)

    assert expense1.partial_spends[0] == pytest.approx(0)
    assert expense2.partial_spends[-1] == pytest.approx(0)


def test_not_enough_budget_to_cover_min_expenses_raises_error():
    expense = Expense(
        description=item01,
        due_date=pendulum.date(2023, 1, 31),
        priority=Priority.LOW,
        range=ExpenseRange(900, 1200, 1000),
        mandatory=True,
    )
    budget = Budget(
        initial=100, recorrent=500, recurrence=30, last_recurrence=0, iterations=1
    )
    portfolio = Portfolio(expenses=[expense], budget=budget)

    params = OptmizationParameters(
        priority_exponent=2, deviation_weight=0, max_time=1000
    )

    with pytest.raises(InfeasibleProblemException):
        Optimizer(
            portfolio=portfolio, parameters=params, start_date=pendulum.date(2023, 1, 1)
        )


def test_full_optimization():
    solution = run_optimization_from_json("test_input.json")
    assert solution["status"] == 0
    assert solution["error"] == ""

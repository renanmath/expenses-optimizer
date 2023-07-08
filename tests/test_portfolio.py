import pytest
import pendulum
from expenses_opt.models.expense import (
    build_expenses_from_csv,
)
from expenses_opt.models.portfolio import (
    Budget,
    Portfolio,
    build_budget_from_parameters,
)
from expenses_opt.utils.utils import get_date_from_string


@pytest.fixture
def budget_factory():
    def make_budget(
        initial: float = 500,
        recorrent: float = 4000,
        recurrence: int = 30,
        last_recurrence: pendulum.Date = pendulum.date(2023, 6, 5),
        iterations: int = 2,
    ):

        budget = Budget(initial, recorrent, recurrence, last_recurrence, iterations)
        return budget

    return make_budget


def test_total_budget(budget_factory):
    budget = budget_factory()
    assert budget.total_budget == 4500


def test_build_budget_from_parameters():
    my_params = {
        "initial": 500,
        "recorrent": 4000,
        "recurrence": 30,
        "last_recurrence": "2023-06-05",
        "iterations": 3,
    }

    start_date = get_date_from_string("2023-06-11")

    budget = build_budget_from_parameters(my_params, start_date)

    assert budget.total_budget == 8500


def test_build_portfolio(budget_factory):
    budget = budget_factory()
    expenses = build_expenses_from_csv("csv_test.csv")
    portfolio = Portfolio(expenses, budget)
    assert portfolio.mandatory_total_min_spend == 570

import pendulum
from expenses_opt.models.expense import (
    build_expenses_from_csv,
    build_expenses_from_dict,
)
from expenses_opt.models.portfolio import (
    build_budget_from_parameters,
    Portfolio,
)
from expenses_opt.optimization.optimizer import OptmizationParameters
from dataclasses import dataclass
from expenses_opt.utils.utils import get_date_from_string
from expenses_opt.exceptions import InvalidDataException


@dataclass
class InputData:
    start_date: pendulum.DateTime
    portfolio: Portfolio
    optmization_parameters: OptmizationParameters


def build_input_data(raw_data: dict) -> InputData:
    start_date = get_date_from_string(raw_data["start_date"])
    budget = build_budget_from_parameters(
        params=raw_data["budget"], start_date=start_date
    )

    if "path_to_csv" in raw_data:
        expenses = build_expenses_from_csv(path=raw_data["path_to_csv"])
    elif "expenses" in raw_data:
        expenses = build_expenses_from_dict(expenses_data=raw_data["expenses"])
    else:
        raise InvalidDataException("No expenses information was found in json")

    portfolio = Portfolio(expenses=expenses, budget=budget)

    max_due_date = max(
        exp.due_date for exp in portfolio.expenses if exp.due_date is not None
    )
    for expense in portfolio.expenses:
        if expense.due_date is None:
            expense.due_date = max_due_date

    parameters = OptmizationParameters(**raw_data["optimization_parameters"])

    input_data = InputData(
        start_date=start_date, portfolio=portfolio, optmization_parameters=parameters
    )

    return input_data

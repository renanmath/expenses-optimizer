from typing import Optional
import pendulum
from expenses_opt.models.expense import Expense
from expenses_opt.utils.utils import get_date_from_string


class Budget:
    def __init__(
        self,
        initial: float,
        recorrent: float,
        recurrence: int,
        last_recurrence: int,
        iterations: int,
    ) -> None:

        self.initial = initial
        self.recorrent = recorrent
        self.recurrence = recurrence
        self.last_recurrence = last_recurrence
        self.iterations = iterations

    @property
    def total_budget(self):
        return self.initial + self.recorrent * (self.iterations - 1)

    def __repr__(self) -> str:
        return f"Budget(initial={self.initial}, recorrent={self.recorrent})"


class Portfolio:
    def __init__(self, expenses: list[Expense], budget: Budget) -> None:

        self.expenses = expenses
        self.budget = budget

    @property
    def mandatory_total_min_spend(self):
        return sum(
            expense.range.minimum for expense in self.expenses if expense.mandatory
        )

    def set_expenses_cost(self, costs: list[Optional[float]]):
        for index, value in enumerate(costs):
            my_expense = self.expenses[index]
            my_expense.set_cost_value(value)

    def __repr__(self) -> str:
        return f"Portfolio with {len(self.expenses)} expenses"


def build_budget_from_parameters(params: dict, start_date: pendulum.Date):

    last_recurrence_date = get_date_from_string(params["last_recurrence"])

    if last_recurrence_date is None or start_date is None:
        raise ValueError("Wrong date format")

    period = start_date - last_recurrence_date
    last_recurrence = period.days

    return Budget(
        initial=params["initial"],
        recorrent=params["recorrent"],
        recurrence=params["recurrence"],
        last_recurrence=last_recurrence,
        iterations=params["iterations"],
    )


if __name__ == "__main__":
    my_params = {
        "initial": 500,
        "recorrent": 4000,
        "recurrence": 30,
        "last_recurrence": "05/06/2023",
        "iterations": 3,
    }

    start_date = get_date_from_string("11/06/2023")

    my_budget = build_budget_from_parameters(my_params, start_date)
    print(my_budget)

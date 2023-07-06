import pendulum
import json
from expenses_opt.constants import Priority, OptimizationObjective
from expenses_opt.utils.utils import (
    get_date_from_string,
    get_priority_from_string,
    get_min_price,
    get_max_price,
)
import csv


class ExpenseRange:
    def __init__(self, minimum: float, maximum: float, target: float) -> None:
        if not (0 <= minimum <= target <= maximum):
            raise ValueError("Range must be a valid interval.")

        self.minimum = minimum
        self.maximum = maximum
        self.target = target

    def __repr__(self) -> str:
        return f"[{self.minimum}, {self.target}, {self.maximum}]"


class Expense:
    def __init__(
        self,
        description: str,
        due_date: pendulum.Date,
        priority: Priority,
        range: ExpenseRange,
        mandatory: bool = False,
    ):

        self.description: str = description
        self.due_date: pendulum.Date = due_date
        self.priority: Priority = priority
        self.range: ExpenseRange = range
        self.mandatory: bool = mandatory
        self.__partial_spends: list[float] = list()

    @property
    def cost(self):
        return sum(self.__partial_spends)

    @property
    def partial_spends(self):
        return self.__partial_spends

    @property
    def optimization_value_target(self):
        return {
            OptimizationObjective.TARGET: self.range.target,
            OptimizationObjective.MAX: self.range.maximum,
            OptimizationObjective.MIN: self.range.minimum,
        }

    def add_partial_spend(self, value: float):
        spend_so_far = sum(self.__partial_spends)
        if value + spend_so_far > self.range.maximum:
            raise ValueError(f"Maximum spend achived for expense {self.description}")
        self.__partial_spends.append(value)

    def get_due_date_in_days(self, start: pendulum.Date):
        period = self.due_date - start
        return period.days

    def __repr__(self) -> str:
        return f"{self.description}: {self.range}"


def build_expenses_from_dict(expenses_data: list[dict]) -> list[Expense]:
    expenses: list[Expense] = list()
    for data in expenses_data:
        new_range = ExpenseRange(**data["range"])
        new_expense = Expense(
            description=data["description"],
            due_date=get_date_from_string(data["due_date"], "YYYY-MM-DD"),
            priority=get_priority_from_string(str(data["priority"])),
            mandatory=data["mandatory"],
            range=new_range,
        )
        expenses.append(new_expense)

    return expenses


def build_expenses_from_csv(path: str):

    expenses: list[Expense] = list()

    with open(path, "r") as file:
        csv_reader = csv.reader(file)

        next(csv_reader)

        for row in csv_reader:
            expense = build_expense_from_row(row)
            expenses.append(expense)

    return expenses


def build_expense_from_row(row: list):

    item = row[0]
    due_date = get_date_from_string(row[1])
    min_price = get_min_price(row[2])
    target_price = get_min_price(row[3])
    max_price = get_max_price(row[4])
    priority = get_priority_from_string(row[5])
    mandatory = True if row[6].lower() == "yes" else False

    exp_range = ExpenseRange(minimum=min_price, maximum=max_price, target=target_price)
    my_expense = Expense(
        description=item,
        due_date=due_date,
        priority=priority,
        range=exp_range,
        mandatory=mandatory,
    )

    return my_expense


def parse_expenses_to_dict(expenses: list[Expense], json_path: str = None):
    expenses_dict = {
        "expenses": [
            {
                "description": expense.description,
                "due_date": str(expense.due_date),
                "priority": expense.priority.value,
                "mandatory": expense.mandatory,
                "range": {
                    "minimum": expense.range.minimum,
                    "maximum": expense.range.maximum,
                    "target": expense.range.target,
                },
            }
            for expense in expenses
        ]
    }

    if json_path is not None:
        with open(json_path, "w") as file:
            json.dump(expenses_dict, file, indent=4)

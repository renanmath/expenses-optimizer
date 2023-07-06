import json
from expenses_opt.optimization.optimizer import Optimizer
from expenses_opt.models.input import InputData, build_input_data
from expenses_opt.exceptions import InfeasibleProblemException


def run_optimization(input_data: InputData) -> Optimizer:

    error_msg = ""
    try:
        optimizer = Optimizer(
            portfolio=input_data.portfolio,
            parameters=input_data.optmization_parameters,
            start_date=input_data.start_date,
        )
        status = optimizer.solve_optimization_problem()
    except InfeasibleProblemException as err:
        status = 1
        error_msg = str(err)

    solution_dict = {
        "status": status,
        "expenses": list(
            map(
                lambda expense: {
                    "expense": expense.description,
                    "total_cost": expense.cost,
                    "partial_spends": expense.partial_spends,
                },
                input_data.portfolio.expenses,
            )
        ),
        "error": error_msg,
    }

    return solution_dict


def run_optimization_from_json(path: str):
    with open(path) as file:
        raw_data = json.load(file)

    return run_optimization_from_raw_data(raw_data)

def run_optimization_from_raw_data(raw_data:dict):
    input_data = build_input_data(raw_data)

    return run_optimization(input_data)


if __name__ == "__main__":
    from pprint import pprint

    pprint(run_optimization_from_json(path="input.json"))

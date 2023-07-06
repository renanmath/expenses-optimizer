import pendulum
from expenses_opt.exceptions import InfeasibleProblemException
from expenses_opt.optimization.builder import (
    OptimizerBuilder,
    OptmizationParameters,
)
from expenses_opt.models.portfolio import Portfolio
from expenses_opt.models.expense import Expense


class Optimizer:
    def __init__(
        self,
        portfolio: Portfolio,
        parameters: OptmizationParameters,
        start_date: pendulum.DateTime,
    ) -> None:
        self.__builder: OptimizerBuilder = OptimizerBuilder(
            portfolio, parameters, start_date
        )
        self.__solver = self.__builder.build_optimization_problem()

    @property
    def variables(self):
        return self.__builder.variables

    @property
    def expenses(self) -> list[Expense]:
        return self.__builder.portfolio.expenses

    def solve_optimization_problem(self):
        status = self.__solver.Solve()

        if status in [self.__solver.FEASIBLE, self.__solver.OPTIMAL]:
            self.build_solution_from_solver()
        else:
            raise InfeasibleProblemException(
                "Optimizer did not found a feasible solution"
            )

        return status

    def build_solution_from_solver(self):
        for i_index, expense in enumerate(self.expenses):
            for j_index in range(self.__builder.iterations):
                expense.add_partial_spend(
                    round(self.variables["x"][i_index][j_index].solution_value(), 2)
                )

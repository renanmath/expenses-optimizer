import pendulum
from expenses_opt.models.portfolio import Portfolio
from ortools.linear_solver import pywraplp

from expenses_opt.constants import OptimizationObjective
from expenses_opt.exceptions import (
    InfeasibleProblemException,
    InvalidDataException,
)


# TODO use dataclass
class OptmizationParameters:
    def __init__(
        self,
        priority_exponent: float,
        deviation_weight: float,
        max_time: float,
    ) -> None:

        if priority_exponent < 1:
            raise InvalidDataException(
                "Priority exponent must be equal or greater than 1"
            )

        if deviation_weight < 0:
            raise InvalidDataException("Weight must be a positive float")

        if max_time < 0:
            raise InvalidDataException("Max optimization time must be a positive float")

        self.priority_exponent = priority_exponent
        self.deviation_weight = deviation_weight
        self.max_time = max_time


class OptimizerBuilder:
    def __init__(
        self,
        portfolio: Portfolio,
        parameters: OptmizationParameters,
        start_date: pendulum.Date,
        objective: OptimizationObjective = OptimizationObjective.TARGET,
    ) -> None:

        self.portfolio = portfolio
        self.parameters = parameters
        self.start_date = start_date
        self.__op_objective = objective

        self.variables = {"x": list(), "y": list(), "epsilon": list()}

        self.__check_feasibility()

    @property
    def num_expenses(self):
        return len(self.portfolio.expenses)

    @property
    def iterations(self):
        return self.portfolio.budget.iterations

    def __check_feasibility(self):
        if (
            self.portfolio.mandatory_total_min_spend
            > self.portfolio.budget.total_budget
        ):
            raise InfeasibleProblemException(
                "Not enough budget to attend all mandatory expenses"
            )

    def build_optimization_problem(self):
        solver = pywraplp.Solver.CreateSolver("CBC")

        solver.SetTimeLimit(self.parameters.max_time)

        self.create_variables(solver=solver)

        self.set_constraints(solver=solver)

        self.set_objective_function(solver=solver)

        return solver

    def create_variables(self, solver):
        # x variables
        for i_index in range(self.num_expenses):
            self.variables["x"].append([])
            for j_index in range(self.iterations):
                var_name = f"x[{i_index}, {j_index}]"
                max_value = self.portfolio.expenses[i_index].range.maximum
                x_var = solver.NumVar(0, max_value, var_name)
                self.variables["x"][i_index].append(x_var)

        # y variables
        for i_index in range(self.num_expenses):
            var_name = f"y[{i_index}]"
            y_var = solver.IntVar(0, 1, var_name)
            self.variables["y"].append(y_var)

        # epsilon variables
        for i_index in range(self.num_expenses):
            var_name = f"epsilon[{i_index}]"
            e_var = solver.NumVar(0, solver.infinity(), var_name)
            self.variables["epsilon"].append(e_var)

    def set_constraints(self, solver):

        print("Setting constraints")
        self.constraint_total_spend_respect_max_cost(solver=solver)
        self.constraint_respect_min_cost(solver=solver)
        self.constraint_partial_spends_respect_due_date(solver=solver)
        self.constraint_total_spend_respect_iteration_budget(solver=solver)
        self.constraint_absolute_error_definition(solver=solver)
        self.constraint_mandatory_expenses_must_be_attended(solver=solver)

    def set_objective_function(self, solver):
        objective = solver.Objective()

        big_c = self.parameters.priority_exponent
        big_a = self.parameters.deviation_weight

        for i_index in range(self.num_expenses):
            e_i = self.variables["epsilon"][i_index]
            y_i = self.variables["y"][i_index]
            p_i = self.portfolio.expenses[i_index].priority.value

            objective.SetCoefficient(e_i, 1 / (p_i**big_c))
            objective.SetCoefficient(y_i, big_a)

        objective.SetMinimization()

    def constraint_total_spend_respect_max_cost(self, solver):
        # \sum_{j=0}^M x_{i,j} <= \overline{g}_i
        for i_index in range(self.num_expenses):
            max_spend = self.portfolio.expenses[i_index].range.maximum

            constraint = solver.Constraint(-solver.infinity(), 0)
            y_i = self.variables["y"][i_index]
            constraint.SetCoefficient(y_i, -max_spend)

            for j_index in range(self.iterations):
                x_i_j = self.variables["x"][i_index][j_index]
                constraint.SetCoefficient(x_i_j, 1)

    def constraint_respect_min_cost(self, solver):
        # \sum_{j=0}^M x_{i,j}  - y_i \cdot \underline{g}_i >= 0
        for i_index in range(self.num_expenses):
            constraint = solver.Constraint(0, solver.infinity())
            y_i = self.variables["y"][i_index]
            min_spend = self.portfolio.expenses[i_index].range.minimum
            constraint.SetCoefficient(y_i, -min_spend)

            for j_index in range(self.iterations):
                x_i_j = self.variables["x"][i_index][j_index]
                constraint.SetCoefficient(x_i_j, 1)

    def constraint_partial_spends_respect_due_date(self, solver):
        # x_{i,j} = 0 \,\,\, \textit{se } \, d_i < \delta - \delta_0 + (j-1) \cdot \delta

        for i_index in range(self.num_expenses):
            for j_index in range(self.iterations):
                expense_due_date = self.portfolio.expenses[i_index].due_date
                period = expense_due_date - self.start_date
                due_date_in_days = period.days
                delta = self.portfolio.budget.recurrence
                delta_0 = self.portfolio.budget.last_recurrence

                if due_date_in_days < delta - delta_0 + (j_index - 1) * delta:
                    x_i_j = self.variables["x"][i_index][j_index]
                    constraint = solver.Constraint(0, 0)
                    constraint.SetCoefficient(x_i_j, 1)

    def constraint_total_spend_respect_iteration_budget(self, solver):
        for k_index in range(self.iterations):
            b_0 = self.portfolio.budget.initial
            b = self.portfolio.budget.recorrent
            max_budget = b_0 + b * k_index

            constraint = solver.Constraint(0, max_budget)

            for i_index in range(self.num_expenses):
                for j_index in range(k_index + 1):
                    x_i_j = self.variables["x"][i_index][j_index]
                    constraint.SetCoefficient(x_i_j, 1)

    def constraint_absolute_error_definition(self, solver):

        # lower constraint
        for i_index in range(self.num_expenses):
            target_value = self.portfolio.expenses[i_index].optimization_value_target[
                self.__op_objective
            ]
            constraint = solver.Constraint(target_value, solver.infinity())

            e_i = self.variables["epsilon"][i_index]
            constraint.SetCoefficient(e_i, target_value)

            for j_index in range(self.iterations):
                x_i_j = self.variables["x"][i_index][j_index]
                constraint.SetCoefficient(x_i_j, 1)

        # upper constraint
        for i_index in range(self.num_expenses):
            target_value = self.portfolio.expenses[i_index].optimization_value_target[
                self.__op_objective
            ]
            constraint = solver.Constraint(-solver.infinity(), target_value)

            e_i = self.variables["epsilon"][i_index]
            constraint.SetCoefficient(e_i, -target_value)

            for j_index in range(self.iterations):
                x_i_j = self.variables["x"][i_index][j_index]
                constraint.SetCoefficient(x_i_j, 1)

    def constraint_mandatory_expenses_must_be_attended(self, solver):
        for i_index in range(self.num_expenses):
            y_i = self.variables["y"][i_index]
            f_i = int(self.portfolio.expenses[i_index].mandatory)

            constraint = solver.Constraint(f_i, 1)
            constraint.SetCoefficient(y_i, 1)

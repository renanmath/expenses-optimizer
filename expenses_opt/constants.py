from enum import Enum


class Priority(Enum):
    HIGHT = 1
    MEDIUM = 2
    LOW = 3


class OptimizationObjective(Enum):
    TARGET = "target"
    MIN = "minumum"
    MAX = "maximum"

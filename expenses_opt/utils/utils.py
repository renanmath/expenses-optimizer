import csv
import pendulum
from expenses_opt.constants import Priority


def get_float_from_string(s: str):
    try:
        return float(s.strip())
    except ValueError:
        return None


def get_priority_from_string(s: str):
    try:
        p_int = int(s)
        p_enum = next((e for e in Priority if e.value == p_int), Priority.LOW)
        return p_enum
    except ValueError:
        return Priority.LOW


def get_date_from_string(str_date: str, format: str = "YYYY-MM-DD"):
    try:
        return pendulum.from_format(str_date, format).date()
    except ValueError:
        return None


def get_min_price(my_string: str):
    min_price = get_float_from_string(my_string)
    return min_price if min_price is not None else 0


def get_max_price(my_string: str):
    max_price = get_float_from_string(my_string)
    return max_price if max_price is not None else float("inf")

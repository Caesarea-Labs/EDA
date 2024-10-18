

from functools import wraps
import math
import time
from typing import Any, Callable, Iterable, Optional, TypeVar, cast

from matplotlib.pylab import f


T = TypeVar("T")
def none_check(value: Optional[T]) -> T:
    assert value is not None, "Expected value to not be None"
    return value

def measure_time(func: Callable[..., T]) -> Callable[..., T]:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        print(f"Executing {func.__name__}()...")
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__}() completed in {end_time - start_time:.4f} seconds.")
        return result
    return wrapper


R = TypeVar('R', int, float)  # The type of the result (int or float)

def max_of(arr: list[T], key: Callable[[T], R]) -> R:
    """
    Returns the maximum value in the array given by the key
    """
    assert len(arr) > 0
    max = -math.inf
    for element in arr:
        value = key(element)
        if value > max:
            max = value
    return cast(R, max)

def min_of(arr: list[T], key: Callable[[T], R]) -> R:
    """
    Returns the minimum value in the array given by the key
    """
    assert len(arr) > 0
    min = math.inf
    for element in arr:
        value = key(element)
        if value < min:
            min = value
    return cast(R, min)

def average_of(arr: list[T], key: Callable[[T], float]) -> float:
    return sum_of(arr, key) / len(arr)

def sum_of(arr: list[T],  key: Callable[[T], float]) -> float:
    sum = 0
    for item in arr:
        sum += key(item)
    return sum

def find(arr: Iterable[T], key: Callable[[T], bool]) -> Optional[T]:
    for item in arr:
        if key(item):
            return item
    return None

def distinct(arr: list[T]) -> list[T]:
    """
    Returns all distinct values of the array, by checking their equality. 
    """
    existing = set()
    result = []
    for element in arr:
        if element not in existing:
            result.append(element)
            existing.add(element)

    return result

def equals_roughly(numA: float, numB: float, precision_decimal_points: int = 10) -> bool:
    """
    Check if two floating-point numbers are approximately equal up to a specified number of decimal places.

    Args:
        numA (float): The first number to compare.
        numB (float): The second number to compare.
        precision_decimal_points (int, optional): The number of decimal places to consider. Defaults to 10.

    Returns:
        bool: True if the numbers are approximately equal up to the specified precision, False otherwise.
    """
    roundedA = round(numA, precision_decimal_points)
    roundedB = round(numB, precision_decimal_points)
    return roundedA == roundedB
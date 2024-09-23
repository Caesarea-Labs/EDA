

from functools import wraps
import math
import time
from typing import Any, Callable, Optional, TypeVar, cast

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
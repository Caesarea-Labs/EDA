

from functools import wraps
import time
from typing import Any, Callable, Optional, TypeVar


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



import os
import functools
from pathlib import Path
import pickle
from time import sleep
import time
from typing import Optional, ParamSpec, TypeVar, Callable, Any

cache_dir = Path("cache")

R = TypeVar('R')
P = ParamSpec('P')

def cached(key: Optional[str] = None) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Decorator to cache the result of a function. If `key` is not provided,
    the function's name is used as the key.

    Args:
        key: An optional string to be used as the cache key.

    Returns:
        A decorator that caches the result of the function.
    """
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        used_key = key or func.__name__
        call_name = f"{func.__name__}() with key {key}" if key is not None else func.__name__
        cache_file = os.path.join(cache_dir, f"{used_key}.pkl")

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            if os.path.exists(cache_file):
                with open(cache_file, 'rb') as f:
                    print(f"Using cached value for {call_name}")
                    result = pickle.load(f)
            else:
                print(f"Executing {call_name} for the first time...")
                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()
                with open(cache_file, 'wb') as f:
                    pickle.dump(result, f)
                print(f"{call_name} completed and cached in {end_time - start_time:.4f} seconds.")
            return result

        return wrapper

    return decorator
    

@cached()
def test_func() -> int: 
    sleep(2)
    return 400

if __name__ == "__main__":
    print(test_func())
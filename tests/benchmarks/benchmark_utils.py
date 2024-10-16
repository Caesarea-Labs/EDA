import time
from typing import Any, Callable, cast

from numpy import average

from eda.utils import max_of


def benchmark(name: str, code: Callable[[], Any], iterations: int = 10):
    """
    Run the code a specified number of times, measuring the average time it takes, and the maximum deviation from the average.
    """
    results: list[float] = []
    for _ in range(iterations):
        start_time = time.time()
        code()
        results.append(time.time() - start_time)

    avg = average(results)
    max_deviation = max_of(results, key=lambda result: cast(float, abs(result - avg)))

    print(f"Benchmark results for {name}: {avg} +-{max_deviation} seconds")


def blackhole(*args):
    """
    Similar to the JMH BlackHole class, this helps ensure a result of a computation is not 'optimized out'
    """
    pass
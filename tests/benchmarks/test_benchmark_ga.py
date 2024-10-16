
from eda.genetic_via_placement import get_test_ga_circuit_edit
from benchmark_utils import benchmark

# @measure_time
def test_benchmark_geneticalgorithm2():
    benchmark(
        "Polygon.intersects",
        lambda: get_test_ga_circuit_edit(plot = False, cache = False, population_size=100, generations=300),
        iterations=3
    )

    # time = timeit.timeit(, number = 3,globals = globals())

    
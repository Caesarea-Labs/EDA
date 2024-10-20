from math import exp
from pathlib import Path
import random
from typing import cast

from shapely import Point, Polygon, STRtree, box

from eda.cache import cached
from eda.circuitedit import circuit_edit
from eda.circuitedit.circuit_edit import CircuitEdit, EditedLayout
from eda.circuitedit.ce_utils import calculate_signal_bounds
from eda.circuitedit.circuit_edit_via import random_point
from eda.circuitedit.genetic_utils import sample_random_point
from eda.circuitedit.layout_ga_utils import get_metal_count_above_polygon, index_layout_metals, index_layout_signal_by_layer
from eda.gds_to_layout import get_corner_gds_layout_test
from eda.geometry.geometry_utils import PolygonIndex, distance, max_distance_between_points
from eda.layout import Layout, Metal, Via
from eda.ui.pyvista_gui import plot_layout_with_qt_gui
import numpy as np
import cv2
from numpy.typing import NDArray
from geneticalgorithm2 import geneticalgorithm2 as ga
import matplotlib.pyplot as plt
from geneticalgorithm2 import Generation
from geneticalgorithm2.data_types.result import GAResult
from geneticalgorithm2 import GeneticAlgorithm2

from eda.geometry.geometry import Point2D, Polygon2D, Rect2D
from eda.utils import none_check

resolution = 100


bound_misses = 0
total_checks = 0
optional_model: GeneticAlgorithm2 | None = None


def generate_initial_cut_population(layout: Layout, population_size: int, signal: int) -> NDArray[np.float64]:
    """
    Returns a 2d float array composing the initial tested points.
    The array has 3 columns, as follows:
    [
        [x, y, layer],
        ...
    ]
    Where (x, y, layer) is a random point on the first signal.
    """
    signal_a_polygons = [(metal.polygon, none_check(metal.layer)) for metal in layout.metals if metal.signal_index == signal]

    # Simple as that
    return np.array(
        [random_point(signal_a_polygons) for _ in range(population_size)]
    )


def create_cut(x: float, y: float, signal_polygons: PolygonIndex[Metal]) -> Polygon:
    """
    Creates a polygon that is the area of a metal that will be removed with a cut, if we target a specific x,y point. 
    """
    raise AssertionError("TODO")


def run_circuit_edit_cut(layout: Layout, signal: int, plot: bool = True, cache: bool = True,

                         population_size: int = 100, generations: int = 100) -> EditedLayout:
    cut_width = 0.2

    # Setup all indices for fast access
    all_metals = index_layout_metals(layout)
    signal_metals_by_layer = index_layout_signal_by_layer(layout, signal)

    def cost_impl(x: float, y: float, layer: int, signal_index: list[PolygonIndex[Metal]]) -> float:
        # Construct a via to see what it would intersect with if this spot would have been chosen
        potential_cut = create_cut(x, y, signal_index[layer])
        # Only metals above this via pose a problem
        intefering_metals_cost = get_metal_count_above_polygon(potential_cut, layer, all_metals)

        # Measure how much of the via actually connects to the target signal.
        connection_to_signal = signal_index[layer].get_intersection(potential_cut).area

        # If the cut is located exactly on the signal then connection_to_signal = cut_width^2 and this value will be 0
        # If the cut is partially on the signal this value will be some high value
        # If the cut is not on this signal this value will be infinity
        connection_cost = 100 * (cut_width ** 2 / connection_to_signal) - 100 if connection_to_signal > 0 else np.Infinity

        # We want connection_cost to be 0 (very important) and intefering_metals_cost to be 0 (important but less so)
        return connection_cost + intefering_metals_cost

    def cost_func(X: NDArray[np.float64]) -> float:
        x = X[0]
        y = X[1]
        z = int(X[2])
        return cost_impl(x, y, z, signal_metals_by_layer)

    @cached("20", enabled=cache)
    def ga_test() -> list[float | int]:
        initial_population = generate_initial_cut_population(layout, population_size, signal)

        algorithm_param = {
            'max_num_iteration': generations,
            'population_size': population_size,
            'mutation_probability': 0.1,
            'elit_ratio': 0.01,
            'parents_portion': 0.3,
            'crossover_type': 'uniform',
            'max_iteration_without_improv': None
        }

        signal_bounds = calculate_signal_bounds(layout, signal).shrink2D_symmetrical(cut_width).to_numpy_array()

        model = ga(dimension=6, variable_type=('real', 'real', 'int', 'real', 'real', 'int'),
                   variable_boundaries=signal_bounds, algorithm_parameters=algorithm_param)
        print("Running GA...")

        result = model.run(progress_bar_stream=None, no_plot=True, function=cost_func, function_timeout=1000,
                           start_generation=Generation(variables=initial_population, scores=None))
        global optional_model
        optional_model = model
        return result.variable.tolist()

    result = ga_test()

    def build_via_at(x: float, y: float, z: float) -> Via:
        rect = Rect2D(x - cut_width / 2, x + cut_width / 2, y - cut_width / 2, y + cut_width / 2)
        return Via(rect, bottom_layer=round(z), top_layer=layout.layer_count(), mark=True)
    via_1 = build_via_at(result[0], result[1], result[2])
    via_2 = build_via_at(result[3], result[4], result[5])

    # new_layout = layout.with_added_vias([via_1, via_2])

    if plot and optional_model is not None:
        none_check(optional_model).plot_results()

    return EditedLayout(
        layout,
        CircuitEdit(
            via_insertions=[via_1, via_2],
            cuts=[]
        )
    )


def get_test_ga_circuit_edit_cut(signal: int = 5,  plot: bool = True, cache: bool = True, population_size: int = 100, generations: int = 300) -> EditedLayout:
    return run_circuit_edit_cut(get_corner_gds_layout_test(), signal, plot, cache, population_size, generations)
    # plot_layout_with_qt_gui(new_layout)


# if __name__ == "__main__":

    # last_generation = none_check(result.last_generation.variables)

    # x1 = [result.variable[0]]
    # y1 = [result.variable[1]]
    # x2 = [result.variable[3]]
    # y2 = [result.variable[4]]

    # polygons = [
    #     point for metal in layout.metals
    #     for point in metal.polygon
    # ]
    # plt.xlim(min_of(polygons, lambda p: p.x), max_of(polygons, lambda p: p.x))
    # plt.ylim(min_of(polygons, lambda p: p.y), max_of(polygons, lambda p: p.y))
    # plt.plot(x1, y1, '*r', x2, y2, '*b')
    # plt.show()

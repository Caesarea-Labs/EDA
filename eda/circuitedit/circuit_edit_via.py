from pathlib import Path
import random
from typing import cast

from shapely import Point, Polygon, STRtree, box

from eda.cache import cached
from eda.circuitedit import circuit_edit
from eda.circuitedit.circuit_edit import CircuitEdit, EditedLayout
from eda.circuitedit.ce_utils import calculate_signal_bounds
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
def random_point(polygon_list: list[tuple[list[Point2D], int]]) -> list[float]:
    polygon, layer = random.choice(polygon_list)
    point = sample_random_point(polygon)
    return [point.x, point.y, layer]

def generate_initial_via_population(layout: Layout, population_size: int, target_signal_a: int, target_signal_b: int) -> NDArray[np.float64]:
    """
    Returns a 2d float array composing the initial tested points.
    The array has 6 columns, as follows:
    [
        [x_a, y_a, layer_a,  x_b, y_b, layer_b],
        ...
    ]
    Where (x_a, y_a, layer_a) is a random point on the first signal, and (x_b, y_b, layer_b) is a random point on the second signal.
    """
    signal_a_polygons = [(metal.polygon, none_check(metal.layer)) for metal in layout.metals if metal.signal_index == target_signal_a]
    signal_b_polygons = [(metal.polygon, none_check(metal.layer)) for metal in layout.metals if metal.signal_index == target_signal_b]



    # Simple as that
    return np.array(
        [random_point(signal_a_polygons) + random_point(signal_b_polygons) for _ in range(population_size)]
    )

optional_model: GeneticAlgorithm2 | None = None


def run_circuit_edit_via(layout: Layout, plot: bool = True, cache: bool = True,
                     signal_a: int = 0, signal_b: int = 5,
                     population_size: int = 100, generations: int = 300) -> EditedLayout:
    via_size = 0.2
    via_padding = 0.2
 # Setup all indices for fast access
    all_metals = index_layout_metals(layout)
    signal_a_metals_by_layer = index_layout_signal_by_layer(layout, signal_a)
    signal_b_metals_by_layer = index_layout_signal_by_layer(layout, signal_b)

    def cost_reward(x: float, y: float, layer: int, signal_index: list[PolygonIndex[Metal]]) -> tuple[float, float]:
        # Construct a via to see what it would intersect with if this spot would have been chosen
        potential_via = box(x - via_size / 2, y - via_size / 2, x + via_size / 2, y + via_size / 2)
        # Only metals above this via pose a problem
        cost = get_metal_count_above_polygon(potential_via, layer, all_metals) 

        # Measure how much of the via actually connects to the target signal.
        connection_to_signal = signal_index[layer].get_intersection(potential_via)
        #  If the via doesn't intersect with the signal at all, this would be 0 and a via here will not be considered.
        # If it does intersect but partially, this will have a small value,
        # If it fully intersects, this will have the maximum possible vaue.
        # Divide by via_size^2 to normalize the value compared to the best result, which is via_size^2.
        reward = connection_to_signal.area / (via_size ** 2)
        return cost, reward

    all_points = [point for metal in layout.metals for point in metal.polygon]
    max_distance = max_distance_between_points(all_points)

    def cost_func(X: NDArray[np.float64]) -> float:
        x1 = X[0]
        y1 = X[1]
        l1 = int(X[2])
        x2 = X[3]
        y2 = X[4]
        l2 = int(X[5])
        cost1, reward1 = cost_reward(x1, y1, l1, signal_a_metals_by_layer)
        cost2, reward2 = cost_reward(x2, y2, l2, signal_b_metals_by_layer)
        cost = cost1+cost2
        # Give higher priority to getting a good connection
        reward = (reward1+reward2) * 5

        if (cost > 0 or reward1 == 0 or reward2 == 0):
            return cost
        else:
            d_cost = distance_cost(x1, y1, x2, y2)
            return -reward + d_cost
            # + alpha*L_cost

    def distance_cost(x1: float, y1: float, x2: float, y2: float) -> float:
        d = distance(x1, y1, x2, y2)
        # We optimize such that the distance will be as close as possible to via_size + via_padding.
        # Divide by max_distance to normalize the value to the problem size.
        return abs(d - (via_size + via_padding)) / max_distance

    @cached("20", enabled=cache)
    def ga_test() -> list[float | int]:
        initial_population = generate_initial_via_population(layout, population_size, signal_a, signal_b)

        algorithm_param = {
            'max_num_iteration': generations,
            'population_size': population_size,
            'mutation_probability': 0.1,
            'elit_ratio': 0.01,
            'parents_portion': 0.3,
            'crossover_type': 'uniform',
            'max_iteration_without_improv': None}

        signal_a_bounds = calculate_signal_bounds(layout, signal_a).shrink2D_symmetrical(via_size).to_numpy_array()
        signal_b_bounds = calculate_signal_bounds(layout, signal_b).shrink2D_symmetrical(via_size).to_numpy_array()
        variable_bounds = np.concatenate((signal_a_bounds, signal_b_bounds), axis=0)

        model = ga(dimension=6, variable_type=('real', 'real', 'int', 'real', 'real', 'int'),
                   variable_boundaries=variable_bounds, algorithm_parameters=algorithm_param
                   )
        print("Running GA...")

        result = model.run(progress_bar_stream=None, no_plot=True, function=cost_func, function_timeout=1000,
                           start_generation=Generation(variables=initial_population, scores=None))
        global optional_model
        optional_model = model
        return result.variable.tolist()

    result = ga_test()

    def build_via_at(x: float, y: float, z: float) -> Via:
        rect = Rect2D(x - via_size / 2, x + via_size / 2, y - via_size / 2, y + via_size / 2)
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


def get_test_ga_circuit_edit(plot: bool = True, cache: bool = True, signal_a: int = 0, signal_b: int = 5, population_size: int = 100, generations: int = 300) -> EditedLayout:
    return run_circuit_edit_via(get_corner_gds_layout_test(), plot, cache, signal_a, signal_b, population_size, generations)
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

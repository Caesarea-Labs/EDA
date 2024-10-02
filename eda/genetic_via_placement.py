from pathlib import Path
import random
from typing import cast

from gdstk import Polygon
from shapely import STRtree, box

from eda.ui.pyvista_gui import plot_layout_with_qt_gui
from .cache import cached
from .gds_to_layout import get_large_gds_layout_test, parse_gds_layout
from .genetic_utils import sample_random_point
from .geometry.geometry import Point2D, Polygon2D, Rect2D, create_polygon
from .geometry.geometry_utils import PolygonIndex, distance, max_distance_between_points
from .layout import Layout, Metal, Via, to_shapely_polygon
import numpy as np
import cv2
from numpy.typing import NDArray
from geneticalgorithm2 import geneticalgorithm2 as ga
import matplotlib.pyplot as plt
from geneticalgorithm2 import Generation
from geneticalgorithm2.data_types.result import GAResult
from geneticalgorithm2 import GeneticAlgorithm2

from .utils import max_of, min_of, none_check

resolution = 100


def Generate_Initial_Population(layout: Layout, population_size: int, target_signal_a: int, target_signal_b: int) -> NDArray[np.float64]:
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

    def random_point(polygon_list: list[tuple[list[Point2D], int]]) -> list[float]:
        polygon, layer = random.choice(polygon_list)
        point = sample_random_point(polygon)
        return [point.x, point.y, layer]

    # Simple as that
    return np.array(
        [random_point(signal_a_polygons) + random_point(signal_b_polygons) for _ in range(population_size)]
    )



def get_test_ga_circuit_edit() -> Layout:
    via_size = 0.2
    via_padding = 0.2
    layout = get_large_gds_layout_test()

    signal_a = 0
    signal_b = 5
    optional_model: GeneticAlgorithm2 | None = None

    def metal_polygon(metal: Metal) -> Polygon2D:
        return metal.polygon
     # Setup all indices for fast access
    all_metals = PolygonIndex([metal for metal in layout.metals], metal_polygon)
    metals_by_layer = layout.metals_by_layer()
    signal_a_metals_by_layer = [
            PolygonIndex([metal for metal in layer_metals if metal.signal_index == signal_a], metal_polygon) for layer_metals in metals_by_layer
    ]
    signal_b_metals_by_layer = [
        PolygonIndex([metal for metal in layer_metals if metal.signal_index == signal_b], metal_polygon) for layer_metals in metals_by_layer
    ]

    def cost_reward(x: float, y: float, layer: int, signal_index: list[PolygonIndex[Metal]]) -> tuple[float, float]:
        # Construct a via to see what it would intersect with if this spot would have been chosen
        potential_via = box(x - via_size / 2, y - via_size / 2, x + via_size / 2, y + via_size / 2)
        # Only metals above this via pose a problem
        obstructing_metals = [metal for metal in all_metals.get_intersecting(potential_via) if none_check(metal.layer) > layer]
        cost = len(obstructing_metals)

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
        # L = ((x1-x2)**2+(y1-y2)**2)**0.5
        # L_cost = (L - 80)**2  # to prevent overlap between the two vias
        # alpha = 0.1
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

    @cached("5")
    def ga_test() -> list[float]:
        def calculate_bounds(layout: Layout) -> list[list[float]]:
            """
            Calculates the area in whcih the GA should generate numbers
            """

            signal_a_polygons = [
                point for metal in layout.metals if metal.signal_index == signal_a
                for point in metal.polygon
            ]
            signal_a_metals = [metal for metal in layout.metals if metal.signal_index == signal_a]

            min_x_a = min_of(signal_a_polygons, lambda p: p.x) + via_size
            min_y_a = min_of(signal_a_polygons, lambda p: p.y) + via_size
            max_x_a = max_of(signal_a_polygons, lambda p: p.x) - via_size
            max_y_a = max_of(signal_a_polygons, lambda p: p.y) - via_size
            min_a_layer = min_of(signal_a_metals, lambda m: none_check(m.layer))
            max_a_layer = max_of(signal_a_metals, lambda m: none_check(m.layer))

            signal_b_polygons = [
                point for metal in layout.metals if metal.signal_index == signal_b
                for point in metal.polygon
            ]
            signal_b_metals = [metal for metal in layout.metals if metal.signal_index == signal_b]

            min_x_b = min_of(signal_b_polygons, lambda p: p.x) + via_size
            min_y_b = min_of(signal_b_polygons, lambda p: p.y) + via_size
            max_x_b = max_of(signal_b_polygons, lambda p: p.x) - via_size
            max_y_b = max_of(signal_b_polygons, lambda p: p.y) - via_size
            min_b_layer = min_of(signal_b_metals, lambda m: none_check(m.layer))
            max_b_layer = max_of(signal_b_metals, lambda m: none_check(m.layer))

            # The bounds for all 6 dimensions of the GA
            return [
                [min_x_a, max_x_a],
                [min_y_a, max_y_a],
                [min_a_layer, max_a_layer],
                [min_x_b, max_x_b],
                [min_y_b, max_y_b],
                [min_b_layer, max_b_layer],
            ]


        # metal_layers = range(layout.layer_count())
        Num_generation = 10000
        # TODO: plot out the result via
        initial_population = Generate_Initial_Population(layout, Num_generation, signal_a, signal_b)







        algorithm_param = {
                        'max_num_iteration': 30,
                        'population_size': Num_generation,
                        'mutation_probability': 0.1,
                        'elit_ratio': 0.01,
                        #    'crossover_probability': 0.5,
                        'parents_portion': 0.3,
                        'crossover_type': 'uniform',
                        'max_iteration_without_improv': None}

        varbound = np.array(calculate_bounds(layout))
        model = ga(dimension=6, variable_type=('real', 'real', 'int', 'real', 'real', 'int'),
                variable_boundaries=varbound, algorithm_parameters=algorithm_param
                )
        # model.set_function_multiprocess(cost_func, n_jobs=-1)
        print("Running GA...")

       

        result = model.run(no_plot=True, function=cost_func, function_timeout=1000, start_generation=Generation(variables= initial_population, scores= None))
        global optional_model
        optional_model = model
        return result.variable.tolist()

    
    result = ga_test()
    def build_via_at(x: float, y: float) -> Via:
        rect = Rect2D(x - via_size / 2, x + via_size / 2, y - via_size / 2, y + via_size / 2)
        return Via(rect, layer = layout.layer_count(), mark=True)
    via_1 = build_via_at(result[0], result[1])
    via_2 = build_via_at(result[3], result[4])

    best_score = cost_func(np.array(result))

    new_layout = layout.with_added_vias([via_1, via_2])
    return new_layout
    # plot_layout_with_qt_gui(new_layout)

    # if optional_model is not None:
    #     cast(GeneticAlgorithm2, optional_model).plot_results()
    






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


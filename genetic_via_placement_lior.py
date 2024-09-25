from pathlib import Path
import random
from typing import cast

from gdstk import Polygon
from shapely import STRtree, box
from gds_to_layout import parse_gds_layout
from genetic_utils import sample_random_point
from geometry.geometry import Point2D, Polygon2D, create_polygon
from geometry.geometry_utils import PolygonIndex
from layout import Layout, Metal, to_shapely_polygon
import numpy as np
import cv2
from numpy.typing import NDArray
from geneticalgorithm import geneticalgorithm as ga
import matplotlib.pyplot as plt

from utils import max_of, min_of, none_check

resolution = 100


def Build_Reward_mask(layout: Layout, bounding_box: Polygon2D, signal_num: int) -> list[NDArray[np.float64]]:
    print({f'signal number is {signal_num}'})
    layer_count = layout.layer_count()
    layers = layout.metals_by_layer()
    x = []
    y = []
    for xy in bounding_box:
        x.append(xy.x)
        y.append(xy.y)
    x_min = min(x)
    x_max = max(x)
    y_min = min(y)
    y_max = max(y)
    w = x_max - x_min
    h = y_max - y_min
    mask_reward_list: list[NDArray[np.float64]] = list()
    for _ in range(layout.layer_count()):
        mask_reward_list.append(np.zeros((w * resolution, h * resolution)))

    min_layer = 1
    max_layer = layer_count
    for layer, metals in enumerate(layers):
        r: cv2.typing.Scalar = cast(cv2.typing.Scalar, (layer - min_layer + 1) / (max_layer - min_layer + 1))
        for metal in metals:
            # I care about the two signals
            if metal.layer != signal_num:
                continue
            polygon = metal.polygon
            ver = []
            for i in range(len(polygon)):
                vertex = polygon[i]
                ver.append([resolution * (vertex.y - y_min), resolution * (vertex.x - x_min)])
            ver = np.array(ver, dtype=int)
            cv2.fillPoly(img=mask_reward_list[layer], pts=[ver], color=r)
    return mask_reward_list


Gausian_Kernal_size = 11


def Build_Cost_mask(layout: Layout, bounding_box: Polygon2D, target_signal_a: int, target_signal_b: int) -> list[NDArray[np.float64]]:
    # chip_signals = self.Chip_BP_Signals_layer_unique2
    layer_count = layout.layer_count()
    x = list()
    y = list()
    for xy in bounding_box:
        x.append(xy.x)
        y.append(xy.y)
    x_min = min(x)
    x_max = max(x)
    y_min = min(y)
    y_max = max(y)
    w = x_max - x_min
    h = y_max - y_min
    mask_cost_list = list()
    for _ in range(layout.layer_count()):
        mask_cost_list.append(np.zeros((w * resolution, h * resolution)))
    # keys = list(chip_signals.cells.keys())
    # keys.remove('check')
    # keys.remove('top_metal')
    min_layer = 1
    max_layer = layer_count

    for layer, metals in enumerate(layout.metals_by_layer()):
        r: cv2.typing.Scalar = cast(cv2.typing.Scalar, (layer - min_layer + 1) / (max_layer - min_layer))
        for metal in metals:
            # I care about other layers
            if metal.layer == target_signal_a or metal.layer == target_signal_b:
                continue

            polygon = metal.polygon
            ver = []
            for i in range(len(polygon)):
                vertex = polygon[i]
                ver.append([resolution * (vertex.y - y_min), resolution * (vertex.x - x_min)])
            ver = np.array(ver, dtype=int)
            cv2.fillPoly(img=mask_cost_list[layer], pts=[ver], color=r)

    cost_mask = list()
    for i in range(len(mask_cost_list)):
        cost_mask.append(cv2.GaussianBlur(mask_cost_list[i], (Gausian_Kernal_size, Gausian_Kernal_size), 0))

    return cost_mask


# def plot_results(bounding_box: CPolygon, X, w):
#     x = list()
#     y = list()
#     for xy in bounding_box:
#         x.append(xy[0])
#         y.append(xy[1])
#     x_min = min(x)
#     x_max = max(x)
#     y_min = min(y)
#     y_max = max(y)
#     x1, y1, l1, x2, y2, l2 = X
#     x1_g = x1 / resolution + x_min
#     y1_g = y1 / resolution + y_min
#     print(f'first via at x={x1_g} and y={y1_g}')
#     x2_g = x2 / resolution + x_min
#     y2_g = y2 / resolution + y_min
#     print(f'Second via at x={x2_g} and y={y2_g}')

#     r = w / resolution
#     res_poly1 = [[x1_g - r, y1_g - r],
#                  [x1_g - r, y1_g + r],
#                  [x1_g + r, y1_g + r],
#                  [x1_g + r, y1_g - r],
#                  [x1_g - r, y1_g - r]]

#     res_poly2 = [[x2_g - r, y2_g - r],
#                  [x2_g - r, y2_g + r],
#                  [x2_g + r, y2_g + r],
#                  [x2_g + r, y2_g - r],
#                  [x2_g - r, y2_g - r]]
#     chip_r =
#     chip_r = gdspy.GdsLibrary(infile='GDS_Signals_global.gds')
#     chip_r.cells[str(int(self.Signals_for_eda[0]))].add(gdspy.Polygon(res_poly1, layer=254))
#     chip_r.cells[str(int(self.Signals_for_eda[1]))].add(gdspy.Polygon(res_poly2, layer=255))
#     chip_r.cells['top_metal'].add(gdspy.Polygon(res_poly1, layer=254))
#     chip_r.cells['top_metal'].add(gdspy.Polygon(res_poly2, layer=255))
#     chip_r.write_gds('GDS_Signals_global_results.gds')
#     chip_r = gdspy.GdsLibrary(infile='GDS_Signals_in_Layers.gds')
#     L1 = 'L-' + str(int(l1))
#     L2 = 'L-' + str(int(l2))
#     chip_r.cells[L1].add(gdspy.Polygon(res_poly1, layer=254))
#     chip_r.cells[L2].add(gdspy.Polygon(res_poly2, layer=255))
#     chip_r.cells['top_metal'].add(gdspy.Polygon(res_poly1, layer=254))
#     chip_r.cells['top_metal'].add(gdspy.Polygon(res_poly2, layer=255))
#     chip_r.write_gds('GDS_Signals_in_Layers_results.gds')


# def Sample_from_poly(polygon: CPolygon, x_g: float, y_g: float, B):
#     x = [point[0] for point in polygon]
#     y = [point[1] for point in polygon]
#     x_min = min(x)
#     x_max = max(x)
#     y_min = min(y)
#     y_max = max(y)
#     x = (np.random.uniform(x_min, x_max)-x_g)*resolution
#     y = (np.random.uniform(y_min, y_max)-y_g)*resolution
#     if (x < B[0, 0]):
#         x = B[0, 0]
#     elif (x > B[0, 1]):
#         x = B[0, 1]
#     if (y < B[1, 0]):
#         y = B[1, 0]
#     elif (y > B[1, 1]):
#         y = B[1, 1]
#     return x, y


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


if __name__ == "__main__":
    via_size = 0.5
    bounds: Polygon2D = create_polygon([(1200, 730), (1200, 775), (1390, 775), (1390, 762), (1210, 762), (1210, 730)])
    layout = parse_gds_layout(
        Path("test_gds_1.gds"),
        bounds,
        metal_layers={61, 62, 63, 64, 65, 66},
        via_layers={70, 71, 72, 73, 74}
    )
    signal_a = 0
    signal_b = 5
    # reward_mask1 = Build_Reward_mask(layout, bounds, signal_num=signal_a)
    # reward_mask2 = Build_Reward_mask(layout, bounds, signal_num=signal_b)
    # cost_mask = Build_Cost_mask(layout, bounds, signal_a, signal_b)
    # cost_mask[0][0]
    # shape = cost_mask[0].shape

    metal_layers = range(layout.layer_count())
    Num_generation = 200
    initial_population = Generate_Initial_Population(layout, Num_generation, signal_a, signal_b)

    def metal_polygon(metal: Metal) -> Polygon2D:
        return metal.polygon

    # Setup all indices for fast access
    all_metals = PolygonIndex([metal for metal in layout.metals], metal_polygon)
    # signal_a_metals = PolygonIndex([metal for metal in layout.metals if metal.signal_index == signal_a], metal_polygon)
    # signal_b_metals = PolygonIndex([metal for metal in layout.metals if metal.signal_index == signal_b], metal_polygon)

    metals_by_layer = layout.metals_by_layer()
    signal_a_metals_by_layer = [
        PolygonIndex([metal for metal in layer_metals if metal.signal_index == signal_a], metal_polygon) for layer_metals in metals_by_layer
    ]
    signal_b_metals_by_layer = [
        PolygonIndex([metal for metal in layer_metals if metal.signal_index == signal_b], metal_polygon) for layer_metals in metals_by_layer
    ]

    algorithm_param = {'initial_population': initial_population,
                       'max_num_iteration': 100,
                       'population_size': Num_generation,
                       'mutation_probability': 0.1,
                       'elit_ratio': 0.01,
                       'crossover_probability': 0.5,
                       'parents_portion': 0.3,
                       'crossover_type': 'uniform',
                       'max_iteration_without_improv': None}

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
        reward = connection_to_signal.area

        # for i in range(layer, len(metal_layers)):
        #     layer_values = cost_mask[i]
        #     start_row = (x-20)
        #     start_col = (x+20)
        #     end_row = (y-20)
        #     end_col = (y+20)
        #     value = layer_values[start_row:start_col, end_row:end_col]
        #     first_sum: NDArray[np.float64] = cast(NDArray[np.float64], sum(value))

        #     cost += sum(first_sum)
        # reward = 0
        # if for_first_signal:
        #     reward = sum(sum(reward_mask1[layer][(x-20):(x+20), (y-20):(y+20)]))  # type: ignore
        #     for i in range(layer, len(metal_layers)):
        #         cost += sum(sum(reward_mask2[i][(x-20):(x+20), (y-20):(y+20)]))  # type: ignore
        # else:
        #     reward = sum(sum(reward_mask2[layer][(x-20):(x+20), (y-20):(y+20)]))  # type: ignore
        #     for i in range(layer, len(metal_layers)):
        #         cost += sum(sum(reward_mask1[i][(x-20):(x+20), (y-20):(y+20)]))  # type: ignore

        return cost, reward

    # TODO: problem right now is that the X,Y values are way off. layer value seems ok.
    def cost_func(X: list[float]):
        x1 = int(X[0])
        y1 = int(X[1])
        l1 = int(X[2])
        x2 = int(X[3])
        y2 = int(X[4])
        l2 = int(X[5])
        cost1, reward1 = cost_reward(x1, y1, l1, signal_a_metals_by_layer)
        cost2, reward2 = cost_reward(x2, y2, l2, signal_b_metals_by_layer)
        cost = cost1+cost2
        reward = 100*(reward1+reward2)
        # L = ((x1-x2)**2+(y1-y2)**2)**0.5
        # L_cost = (L - 80)**2  # to prevent overlap between the two vias
        # alpha = 0.1
        if (cost > 0 or reward1 == 0 or reward2 == 0):
            return cost
        else:
            return -reward
            # + alpha*L_cost

    varbound = np.array(calculate_bounds(layout))
    vartype = np.array([['real'], ['real'], ['int'], ['real'], ['real'], ['int']])
    model = ga(function=cost_func, dimension=6, variable_type_mixed=vartype,
               variable_boundaries=varbound, algorithm_parameters=algorithm_param, function_timeout=1000)
    print("Running GA...")
    model.run()

    x1 = initial_population[:, 0]
    y1 = initial_population[:, 1]
    x2 = initial_population[:, 3]
    y2 = initial_population[:, 4]

    plt.plot(x1, y1, '*r', x2, y2, '*b')
    plt.show()

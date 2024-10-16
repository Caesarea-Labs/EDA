from typing import Callable
from shapely import Polygon
from shapely.ops import unary_union

from benchmark_utils import benchmark, blackhole
from eda.utils import sum_of
from test_intersection_polygons import test_intersection_polygons_const


def shapely_intersect_area_union(polygon_list: list[Polygon], rect: Polygon) -> float:
    """
    Calculates the area that a rectangle intersects with a list of polygons by using unary_union. 
    This has the benefit of working when the polygons intersect between themselves., but is slower. 
    """
    intersecting_subset = [polygon for polygon in polygon_list if rect.intersects(polygon)]
    intersections = [polygon.intersection(rect) for polygon in intersecting_subset]
    union = unary_union(intersections)
    return union.area

def shapely_intersect_area_sum(polygon_list: list[Polygon], rect: Polygon) -> float:
    """
    Calculates the area that a rectangle intersects with a list of polygons by summing the areas of the intersections.
    This has the benefit of being faster, but can provider an incorrect result in the case multiple polygons span the same area as the rectangle. 
    """
    intersecting_subset = [polygon for polygon in polygon_list if rect.intersects(polygon)]
    intersections = [polygon.intersection(rect) for polygon in intersecting_subset]
    return sum_of(intersections, key= lambda poly: poly.area)

def shapely_intersect_area_sum_no_intersects(polygon_list: list[Polygon], rect: Polygon) -> float:
    """
    Calculates the area that a rectangle intersects with a list of polygons by summing the areas of the intersections.
    This has the benefit of being faster, but can provider an incorrect result in the case multiple polygons span the same area as the rectangle. 
    Same as shapely_intersect_area_sum but doesn't filter by intersections first, which may be faster or slower.
    """
    intersections = [polygon.intersection(rect) for polygon in polygon_list]
    return sum_of(intersections, key= lambda poly: poly.area)


# TODO: test they all return the same result in every case!


def shapely_intersect_union_benchmark():
    for rect, polys in test_intersection_polygons_const:
        blackhole(shapely_intersect_area_union(polys, rect))

def shapely_intersect_sum_benchmark():
    for rect, polys in test_intersection_polygons_const:
        blackhole(shapely_intersect_area_sum(polys, rect))

def shapely_intersect_sum_no_intersects_benchmark():
    for rect, polys in test_intersection_polygons_const:
        blackhole(shapely_intersect_area_sum_no_intersects(polys, rect))


def test_benchmark_intersection_area_union():
    benchmark("Shapely intersects area", shapely_intersect_union_benchmark, iterations=10000)

def test_benchmark_intersection_area_sum():
    benchmark("Shapely intersects area", shapely_intersect_sum_benchmark, iterations=10000)

def test_benchmark_intersection_area_sum_no_intersects():
    benchmark("Shapely intersects area", shapely_intersect_sum_no_intersects_benchmark, iterations=10000)

def test_intersections_correctness():
    def test_intersection_area_algorithm(algorithm: Callable[[list[Polygon], Polygon], float]):
        for rect, polys in test_intersection_polygons_const:
            # Use the slowest, most well known to be correct algorithm as a baseline for the result
            baseline = shapely_intersect_area_union(polys, rect)
            algorithm_result = algorithm(polys, rect)
            assert baseline == algorithm_result, f"Algorithm {algorithm} produced an incorrect result: {algorithm_result} instead of {baseline}. Rect: {poly_to_string(rect)}, Polys: {[poly_to_string(poly) for poly in polys]}"

    # test_intersection_area_algorithm(shapely_intersect_area_union)
    test_intersection_area_algorithm(shapely_intersect_area_sum)
    test_intersection_area_algorithm(shapely_intersect_area_sum_no_intersects)


def poly_to_string(poly: Polygon)-> str:
    return str(list(poly.exterior.coords)[:-1])
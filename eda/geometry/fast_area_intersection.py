from numpy import diff
from shapely import Geometry, LineString, Polygon, STRtree, difference, intersects, is_empty, overlaps
import shapely
from eda.geometry.geometry import Point2D, Rect2D, Polygon2D
from rtree import index
from shapely.geometry.base import BaseGeometry

from typing import List, Literal, Optional, Tuple, cast
import bisect

from eda.geometry.shapely_utils import unpack_polygons

Edge = Literal["left", "right", "bottom", "top"]


def intersecting_area(polygon: Polygon2D, polygons: list[Polygon2D]) -> float:
    """
    Efficiently calculates the total area that the convex polygon intersects with the given convex polygons. 
    Assumes the list of polygons don't intersect. To ensure this, call remove_polygon_overlaps.
    Also assumes the list of polygons are convex. To ensure this, call TODO. 
    """
    pass



def intersection(a: Polygon2D, b: Polygon2D) -> Polygon2D:
    """
    Assumes the two polygons are convex.
    """
    output_list: List[Point2D] = a.copy()
    clipper: List[Point2D] = b

    for i in range(len(clipper)):
        input_list = output_list[:]
        output_list = []

        if not input_list:
            break  # No intersection

        # Define the current edge of the clipping polygon
        clip_edge_start = clipper[i]
        clip_edge_end = clipper[(i + 1) % len(clipper)]

        for j in range(len(input_list)):
            current_point = input_list[j]
            prev_point = input_list[j - 1]  # Handles wrap-around

            current_inside = is_inside(current_point, clip_edge_start, clip_edge_end)
            prev_inside = is_inside(prev_point, clip_edge_start, clip_edge_end)

            if current_inside:
                if not prev_inside:
                    # Edge goes from outside to inside; add intersection point
                    intersection_point = compute_intersection(
                        prev_point, current_point, clip_edge_start, clip_edge_end
                    )
                    if intersection_point:
                        output_list.append(intersection_point)
                output_list.append(current_point)
            elif prev_inside:
                # Edge goes from inside to outside; add intersection point
                intersection_point = compute_intersection(
                    prev_point, current_point, clip_edge_start, clip_edge_end
                )
                if intersection_point:
                    output_list.append(intersection_point)

    return Polygon2D(output_list)

def is_inside(p: Point2D, edge_start: Point2D, edge_end: Point2D) -> bool:
    # Determines if point p is inside the half-plane defined by edge_start -> edge_end
    return cross_product(edge_start, edge_end, p) >= 0

def cross_product(a: Point2D, b: Point2D, c: Point2D) -> float:
    # Computes the cross product (b - a) x (c - a)
    return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)

def compute_intersection(
    s1: Point2D, e1: Point2D, s2: Point2D, e2: Point2D
) -> Optional[Point2D]:
    # Computes the intersection point of lines s1-e1 and s2-e2
    denominator = (e1.x - s1.x) * (e2.y - s2.y) - (e1.y - s1.y) * (e2.x - s2.x)
    if abs(denominator) < 1e-10:
        # Lines are parallel or coincident
        return None

    numerator1 = (s1.y - s2.y) * (e2.x - s2.x) - (s1.x - s2.x) * (e2.y - s2.y)
    t1 = numerator1 / denominator

    x = s1.x + t1 * (e1.x - s1.x)
    y = s1.y + t1 * (e1.y - s1.y)
    return Point2D(x, y)

def remove_polygon_overlaps(polygons: list[Polygon]) -> list[Polygon]:
    """
    Returns a list of polygons encompassing the same area, but don't overlap. 
    The amount of result polygons will be about the same, but may be slightly more or less. 
    """
    polygon_index = index.Index()
    for i, polygon in enumerate(polygons):
        polygon_index.add(i, polygon.bounds, obj=polygon)

    # List of polygons that have already been cut or are about to be cut.
    # By only querying from this list, we avoid deleting the same area twice, losing the intersecting area altogether.
    cleaned_polygons: list[BaseGeometry] = cast(list[BaseGeometry], polygons.copy())
    for i in range(len(polygons)):
        current = cleaned_polygons[i]
        # If it encompasses no area it doesn't overlap with anything
        if current.area > 0:
            close_polygons = polygon_index.intersection(current.bounds, objects = True)
            for close_polygon_holder in close_polygons:
                close_polygon = cast(BaseGeometry, close_polygon_holder.object)
                if close_polygon_holder.id != i:
                    overlapping_area = close_polygon.intersection(current)

                    # Only cut overlapping polygons. If they intersect as a 2D line we don't need to do this. 
                    # Checking > 0.000001 is more reliable than >0 because of floating point imprecision
                    if overlapping_area.area >= 0.00000000001:
                        # This polygon intersects, we need to cut it.
                        diff = close_polygon.difference(current)
                        cut_polygon_id = close_polygon_holder.id
                        # Modify the intersecting polygon. 
                        # When we access it later, it will be smaller and won't try removing this part from this polygon ('current' in this context)
                        cleaned_polygons[cut_polygon_id] = diff

                        # Update index to use new polygon
                        polygon_index.delete(cut_polygon_id, coordinates=close_polygon.bounds)
                        # If it's a LineString now we don't need to add it back, it's practically nothing
                        if not diff.is_empty and not isinstance(diff, LineString):
                            polygon_index.add(cut_polygon_id, coordinates=diff.bounds, obj = diff)

            
    # Unpack the possibly multiple polygons that each 'cleaned polygon' includes
    return [polygon for geometry in cleaned_polygons for polygon in unpack_polygons(geometry)]



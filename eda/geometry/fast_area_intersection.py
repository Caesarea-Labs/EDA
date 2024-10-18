from numpy import diff
from shapely import Geometry, LineString, Polygon, STRtree, difference, intersects, is_empty, overlaps
import shapely
from eda.geometry.geometry import Point2D, Rect2D, Polygon2D
from rtree import index
from shapely.geometry.base import BaseGeometry

from typing import List, Literal, Tuple, cast
import bisect

from eda.geometry.shapely_utils import unpack_polygons

Edge = Literal["left", "right", "bottom", "top"]


def intersecting_area(rect: Rect2D, polygons: List[Polygon2D]) -> float:
    """
    Efficiently calculates the total area that the rect intersects with the given polygons. 
    Assumes the list of polygons don't intersect. To ensure this, call 
    """

# TODO: second polygon overlaps with third polygon, see why that part is not getting removed on second iteration.
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



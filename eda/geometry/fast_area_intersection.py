from numpy import diff
from shapely import Geometry, Polygon, STRtree
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

# TODO: didn't work, see chatgpt.
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
        close_polygons = polygon_index.intersection(current.bounds, objects = True)
        for close_polygon_holder in close_polygons:
            close_polygon = cast(BaseGeometry, close_polygon_holder.object)
            if close_polygon.intersects(current):
                # This polygon intersects, we need to cut it.
                difference = close_polygon.difference(current)
                # Modify the intersecting polygon. 
                # When we access it later, it will be smaller and won't try removing this part from this polygon ('current' in this context)
                cleaned_polygons[close_polygon_holder.id] = difference
            
    # Unpack the possibly multiple polygons that each 'cleaned polygon' includes
    return [polygon for geometry in cleaned_polygons for polygon in unpack_polygons(geometry)]



from typing import cast
from shapely import GeometryCollection, LineString, MultiPolygon, Polygon
from shapely.geometry.base import BaseGeometry

from eda.utils import none_check

def unpack_polygons(geometry: BaseGeometry) -> list[Polygon]:
    """
    Returns the list of polygons that compose a shapely geometry.
    """
        # We don't need polygons that intersect so little that the intersection is one dimensional
    if geometry.is_empty or isinstance(geometry, LineString): return []

    # assert not intersection.is_empty, f"Expected polygons {polygon} and {cut_shape} to intersect before cutting them"

    if isinstance(geometry, Polygon):
        geoms = [geometry]
    elif  isinstance(geometry, MultiPolygon):
        geoms = geometry.geoms
    elif isinstance(geometry, GeometryCollection):
        geoms = geometry.geoms
    else:
         assert False, f"Unexpected type of geometry: {geometry}"

    return cast(list[Polygon], geoms)
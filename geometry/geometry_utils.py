from typing import Callable, Generic, TypeVar
from shapely import Polygon as ShapelyPolygon, STRtree
import shapely
from shapely.geometry.base import BaseGeometry
from geometry.geometry import Mesh2D, Point2D, Polygon2D, TriangleIndices
from utils import distinct
import triangle


def triangulate_polygon(polygon: Polygon2D) -> Mesh2D:
    """
    Returns the constrained delaunay triangulation of the given polygon.
    """

    unique_vertices = distinct(polygon)
    vertex_count = len(unique_vertices)
    # Define the S-shaped polygon vertices
    input_vertices = {
        'vertices': [(vertex.x, vertex.y) for vertex in unique_vertices],
        # Every vertex is connected to the next
        'segments': [[i, i + 1 if i < vertex_count - 1 else 0] for i in range(vertex_count)]
    }

    # Compute the Constrained Delaunay Triangulation
    triangulation = triangle.triangulate(input_vertices, 'p')
    vertices = [Point2D(vertex[0], vertex[1]) for vertex in triangulation["vertices"]]
    triangles = [TriangleIndices(tri[0], tri[1], tri[2]) for tri in triangulation["triangles"]]

    return Mesh2D(vertices, triangles)


def to_shapely_polygon(polygon: Polygon2D) -> ShapelyPolygon:
    return ShapelyPolygon([(point.x, point.y) for point in polygon])


T = TypeVar("T")


class PolygonIndex(Generic[T]):
    """
    Allows fast intersection checks by indexing polygons
    """

    tree: STRtree
    items: list[T]
    shapely_polygons: list[ShapelyPolygon]
    polygon_getter: Callable[[T], Polygon2D]

    def __init__(self, items: list[T], polygon_getter: Callable[[T], Polygon2D]) -> None:
        self.items = items
        self.shapely_polygons = [to_shapely_polygon(polygon_getter(item)) for item in items]
        self.tree = STRtree(self.shapely_polygons)

    def get_intersecting(self, polygon: ShapelyPolygon) -> list[T]:
        """
        Returns all elements in the index's list that intersect with the passed polygon
        """

        # This step is very important as it vastly reduces the amount of intersection checks we need to do, essentially making this operation O(1) instead of O(n)
        candidates = self.tree.query(polygon)
        # Query does not guaranetee they all intersect, but it does significantly reduce the amount of checks we need to do.
        indices = [index for index in candidates if polygon.intersects(self.shapely_polygons[index])]

        return [self.items[i] for i in indices]

    def get_intersection(self, polygon: ShapelyPolygon) -> BaseGeometry:
        """
        Returns the portion of the passed polygon that intersects with any of the index's polygon.
        """

        # This step is very important as it vastly reduces the amount of intersection checks we need to do, essentially making this operation O(1) instead of O(n)
        candidates = self.tree.query(polygon)
        # Query does not guaranetee they all intersect, but it does significantly reduce the amount of checks we need to do.
        indices = [index for index in candidates if polygon.intersects(self.shapely_polygons[index])]
        
        return shapely.unary_union([shapely.intersection(self.shapely_polygons[i], polygon) for i in indices])


# def fast_get_intersecting(polygon_cache: STRtree, associated_list: list[T], polygon: ShapelyPolygon) -> list[T]:
#     """
#     Assuming polygon_cache is created from associated_list mapped to a single polygon per item,
#     Efficiently gets the items of the associated_list that their matching polygon intersects with the passed polygon.
#     """

#     # This step is very important as it vastly reduces the amount of intersection checks we need to do, essentially making this operation O(1) instead of O(n)
#     candidates = polygon_cache.query(polygon)
#     indices = []

#     return any(polygon.intersects(metals.geometries[candidate]) for candidate in candidates)

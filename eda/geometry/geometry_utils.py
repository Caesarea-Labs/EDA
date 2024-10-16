from itertools import combinations
from typing import Callable, Generic, TypeVar, cast
import numpy as np
from shapely import Geometry, Polygon as ShapelyPolygon, STRtree, prepare
import shapely
from shapely.geometry.base import BaseGeometry
from ..utils import distinct
from .geometry import Mesh2D, Point2D, Polygon2D, TriangleIndices
import triangle
from scipy.spatial import ConvexHull


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

    # def get_intersection(self, polygon: ShapelyPolygon) -> BaseGeometry:
    #     """
    #     Returns the portion of the passed polygon that intersects with any of the index's polygon.
    #     """

    #     # This step is very important as it vastly reduces the amount of intersection checks we need to do, essentially making this operation O(1) instead of O(n)
    #     candidates = self.tree.query(polygon)
    #     # Query does not guaranetee they all intersect, but it does significantly reduce the amount of checks we need to do.
    #     indices = [index for index in candidates if polygon.intersects(self.shapely_polygons[index])]
        
    #     return shapely.unary_union([shapely.intersection(self.shapely_polygons[i], polygon) for i in indices])
    def get_intersection(self, polygon: ShapelyPolygon) -> BaseGeometry:
        """
        Returns the portion of the passed polygon that intersects with any of the index's polygon.
        """


        # This step is very important as it vastly reduces the amount of intersection checks we need to do, essentially making this operation O(1) instead of O(n)
        candidates = self.tree.query(polygon)
        # test_list.append((polygon, [self.shapely_polygons[i] for i in candidates]))
        # intersections = [intersection_wrapper(polygon,self.shapely_polygons[index]) for index in candidates]
        # filtered = [intersection ]
        # Query does not guaranetee they all intersect, but it does significantly reduce the amount of checks we need to do.
        indices = [index for index in candidates if intersects_wrapper(polygon,self.shapely_polygons[index])]

        
        return union_wrapper([intersection_wrapper(self.shapely_polygons[i], polygon) for i in indices])


    

def intersects_wrapper(poly: ShapelyPolygon, geo: Geometry)-> bool:
    return poly.intersects(geo)

# test_list: list[tuple[ShapelyPolygon, list[Geometry]]] = []
# def format_test_list() -> str:
#     def format_poly_list(geoms: list[Geometry]) -> str:
#         return "\t\t[\n" + ",\n".join([f"\t\t\tPolygon({list(geom.exterior.coords)[:-1]})" for geom in geoms]) + "\n\t\t]"

#     return "[\n" + ",\n".join([f"\t(\n\t\tPolygon({list(rect.exterior.coords)[:-1]}),\n{format_poly_list(poly_list)}\n\t)" for rect, poly_list in test_list]) + "\n]"
def intersection_wrapper(a: Geometry, b: Geometry) -> Geometry:
    return shapely.intersection(a, b)

def union_wrapper(geoms: list[Geometry]) -> BaseGeometry:
    return shapely.unary_union(geoms)

def distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """
    Returns the euclidean distance between two points
    """
    return ((x1-x2)**2+(y1-y2)**2)**0.5

def max_distance_between_points(points: list[Point2D]) -> float:
    """
    Returns the maximum distance between any 2 points in the given list, in O(nlogn) time
    """

    # Convert the list of points into a numpy array
    np_points = np.array([(point.x,point.y) for point in points])
    
    # Compute the convex hull
    hull = ConvexHull(np_points)
    
    # Extract the vertices of the convex hull
    hull_points = np_points[hull.vertices]
    
    # Compute the maximum distance between any pair of hull points
    max_dist = 0
    for p1, p2 in combinations(hull_points, 2):
        dist = cast(float, np.linalg.norm(p1 - p2))  # Euclidean distance
        max_dist = max(max_dist, dist)
    
    return max_dist



# def fast_get_intersecting(polygon_cache: STRtree, associated_list: list[T], polygon: ShapelyPolygon) -> list[T]:
#     """
#     Assuming polygon_cache is created from associated_list mapped to a single polygon per item,
#     Efficiently gets the items of the associated_list that their matching polygon intersects with the passed polygon.
#     """

#     # This step is very important as it vastly reduces the amount of intersection checks we need to do, essentially making this operation O(1) instead of O(n)
#     candidates = polygon_cache.query(polygon)
#     indices = []

#     return any(polygon.intersects(metals.geometries[candidate]) for candidate in candidates)

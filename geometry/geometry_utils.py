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

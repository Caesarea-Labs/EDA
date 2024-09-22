from dataclasses import dataclass
from numpy import poly
import triangle
import matplotlib.pyplot as plt

from layout import Point2D


@dataclass
class Point3D:
    x: float
    y: float
    z: float


@dataclass
class Triangle:
    a_index: int
    b_index: int
    c_index: int


@dataclass
class Mesh:
    vertices: list[Point3D]
    triangles: list[Triangle]
    color: str
    # edge_color: str
    alpha: float
    name: str


@dataclass
class Polygon3D:
    """
    Generic representation of any kind of polygon that spans across multiple z values
    """
    z_base: float
    z_top: float
    vertices: list[Point2D]
    color: str
    # edge_color: str
    alpha: float
    name: str


def polygon_to_mesh(polygon: Polygon3D) -> Mesh:
    vertex_count = len(polygon.vertices)
    # Define the S-shaped polygon vertices
    input_vertices = {
        'vertices': [(vertex.x, vertex.y) for vertex in polygon.vertices],
        # Every vertex is connected to the next
        'segments': [[i, i + 1 if i < vertex_count - 1 else 0] for i in range(vertex_count)]
    }

    # Compute the Constrained Delaunay Triangulation
    triangulation = triangle.triangulate(input_vertices, 'p')

    base_vertices = [Point3D(vertex[0], vertex[1], polygon.z_base) for vertex in triangulation["vertices"]]
    base_triangles = [Triangle(triangle[0], triangle[1], triangle[2]) for triangle in triangulation["triangles"]]

    top_vertices = [Point3D(vertex[0], vertex[1], polygon.z_top) for vertex in triangulation["vertices"]]
    # Make the top triangles match with the top vertices by shifting them to start from the indices of the top vertices.
    top_shift = len(base_vertices)
    top_triangles = [
        Triangle(triangle[0] + top_shift, triangle[1] + top_shift, triangle[2] + top_shift) for triangle in triangulation["triangles"]
    ]

    # Vertices that the side polygons need to to attach to. These are simple to calculate and don't require triangulation.
    side_bottom_vertices = [Point3D(vertex.x, vertex.y, polygon.z_base) for vertex in polygon.vertices]
    side_top_vertices = [Point3D(vertex.x, vertex.y, polygon.z_top) for vertex in polygon.vertices]

    # Get a pointer to the part where we have the side_bottom_vertices
    side_bottom_shift = top_shift + len(top_vertices)
    # Get a pointer to the part where we have the side_top_vertices
    side_top_shift = side_bottom_shift + len(side_bottom_vertices)

    # Sides are composed of rectangles, so we need two triangles for each side
    side_left_triangles = [

        Triangle(
            # Bottom left
            side_bottom_shift + i,
            # Bottom right
            side_bottom_shift + i + 1 if i < vertex_count - 1 else side_bottom_shift,
            # Top left
            side_top_shift + i
        ) for i in range(vertex_count)
    ]

    side_right_triangles = [
        # The order here is very important, something needs to line up with the left triangle part, I'm not quite sure how it works.
        Triangle(
            # Top left
            side_top_shift + i,
            # Bottom right
            side_bottom_shift + i + 1 if i < vertex_count - 1 else side_bottom_shift,
            # Top right
            side_top_shift + i + 1 if i < vertex_count - 1 else side_top_shift,

        )
        for i in range(vertex_count)
    ]

    output_vertices = base_vertices + top_vertices + side_bottom_vertices + side_top_vertices

    output_triangles = base_triangles + top_triangles + side_left_triangles + side_right_triangles

    #  Plot the triangulation
    # plt.triplot(triangulation['vertices'][:, 0], triangulation['vertices'][:, 1], triangulation['triangles'])
    # plt.show()

    return Mesh(output_vertices, output_triangles, color=polygon.color, alpha=polygon.alpha, name=polygon.name)

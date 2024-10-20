from dataclasses import dataclass
from numpy import array, average, poly, unique
import matplotlib.pyplot as plt

from .geometry import Point2D, Point3D, Polygon2D, TriangleIndices
from .geometry_utils import triangulate_polygon
from ..utils import average_of, distinct


@dataclass
class AnnotatedMesh:
    vertices: list[Point3D]
    triangles: list[TriangleIndices]
    color: str
    alpha: float
    name: str
    group_name: str

    def center(self) -> Point3D:
        x = average_of(self.vertices, lambda v: v.x)
        y = average_of(self.vertices, lambda v: v.y)
        z = average_of(self.vertices, lambda v: v.z)
        return Point3D(x, y, z)


@dataclass
class ExtrudedPolygon:
    """
    Generic representation of any kind of polygon that spans across multiple z values
    """
    z_base: float
    z_top: float
    vertices: Polygon2D
    color: str
    alpha: float
    name: str
    group_name: str


problematic_mesh = [
    (1200, 735.22),
    (1200.43, 735.22),
    (1200.43, 735.0),
    (1200.0, 730.0),
    (1200.0, 735.22)
]


def polygon_to_mesh(polygon: ExtrudedPolygon) -> AnnotatedMesh:
    unique_vertices = distinct(polygon.vertices)
    vertex_count = len(unique_vertices)

    # Compute the Constrained Delaunay Triangulation
    triangulation = triangulate_polygon(polygon.vertices)

    base_vertices = [Point3D(vertex.x, vertex.y, polygon.z_base) for vertex in triangulation.vertices]
    base_triangles = triangulation.triangles

    top_vertices = [Point3D(vertex.x, vertex.y, polygon.z_top) for vertex in triangulation.vertices]
    # Make the top triangles match with the top vertices by shifting them to start from the indices of the top vertices.
    top_shift = len(base_vertices)
    top_triangles = [
        TriangleIndices(triangle.a_index + top_shift, triangle.b_index + top_shift, triangle.c_index + top_shift) for triangle in triangulation.triangles
    ]

    # Vertices that the side polygons need to to attach to. These are simple to calculate and don't require triangulation.
    side_bottom_vertices = [Point3D(vertex.x, vertex.y, polygon.z_base) for vertex in unique_vertices]
    side_top_vertices = [Point3D(vertex.x, vertex.y, polygon.z_top) for vertex in unique_vertices]

    # Get a pointer to the part where we have the side_bottom_vertices
    side_bottom_shift = top_shift + len(top_vertices)
    # Get a pointer to the part where we have the side_top_vertices
    side_top_shift = side_bottom_shift + len(side_bottom_vertices)

    # Sides are composed of rectangles, so we need two triangles for each side
    side_left_triangles = [

        TriangleIndices(
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
        TriangleIndices(
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

    return AnnotatedMesh(
        output_vertices, output_triangles, color=polygon.color, alpha=polygon.alpha, name=polygon.name, group_name=polygon.group_name
        )

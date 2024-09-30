from dataclasses import dataclass
from typing import Iterator



@dataclass(frozen=True, eq=True)
class Point2D:
    x: float
    y: float

    def __iter__(self) -> Iterator[float]:
        return iter((self.x, self.y))


Polygon2D = list[Point2D]
"""
A 2d polygon represented by a list of vertices connected in order. 
"""


def create_polygon(points: list[tuple[float, float]]) -> Polygon2D:
    return Polygon2D([Point2D(p[0], p[1]) for p in points])


@dataclass
class Point3D:
    x: float
    y: float
    z: float

    def to_tuple(self) -> tuple[float, float, float]:
        return (self.x, self.y, self.z)


@dataclass
class Rect2D:
    x_start: float
    x_end: float
    y_start: float
    y_end: float

    def as_polygon(self) -> Polygon2D:
        """
        Returns the 4 vertices at the edges of the rectangle
        """
        return [Point2D(self.x_start, self.y_start), Point2D(self.x_end, self.y_start), Point2D(self.x_end, self.y_end),
                Point2D(self.x_start, self.y_end)]


@dataclass
class Triangle2D:
    a: Point2D
    b: Point2D
    c: Point2D

    def area(self) -> float:
        return 0.5 * abs(
            self.a.x * (self.b.y - self.c.y) +
            self.b.x * (self.c.y - self.a.y) +
            self.c.x * (self.a.y - self.b.y)
        )


@dataclass
class TriangleIndices:
    """
    A TriangleIndices references 3 indices of a point array P, representing possible vertices. 
    Then, the coordinates of the 3 vertices of the triangle are P[a_index], P[b_index], P[c_index]
    This is dimension agnostic, meaning this could be 2 dimensional if P has 2d points, and 3 dimension if P has 3d points.
    """
    a_index: int
    b_index: int
    c_index: int


@dataclass
class Mesh2D:
    vertices: list[Point2D]
    triangles: list[TriangleIndices]

    def resolve_triangles(self) -> list[Triangle2D]:
        """
        Returns the actual coordinates of the vertices of the triangles instead of just indices pointing to them
        """
        return [Triangle2D(self.vertices[t.a_index], self.vertices[t.b_index], self.vertices[t.c_index]) for t in self.triangles]

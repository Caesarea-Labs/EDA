from dataclasses import dataclass
from turtle import right
from typing import Iterator
from matplotlib.pylab import f
import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True, eq=True)
class Point2D:
    x: float
    y: float

    def __iter__(self) -> Iterator[float]:
        return iter((self.x, self.y))

    def to_tuple(self) -> tuple[float, float]:
        return (self.x, self.y)


Polygon2D = list[Point2D]
"""
A 2d polygon represented by a list of vertices connected in order. 
"""


def create_polygon(points: list[tuple[float, float]]) -> Polygon2D:
    return Polygon2D([Point2D(p[0], p[1]) for p in points])


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
class Rect3D:
    x: float
    y: float
    z: float
    width: float
    """
    Corresponds to the X value
    """
    length: float
    """
    Corresponds to the Y value
    """
    height: float
    """
    Corresponds to the Z value
    """

    @classmethod
    def from_bounds(cls, x_min: float, x_max: float, y_min: float, y_max: float, z_min: float, z_max: float) -> 'Rect3D':
        return cls(x_min, y_min, z_min, x_max - x_min, y_max - y_min, z_max - z_min)

    @property
    def x_end(self):
        return self.x + self.width
    @property
    def y_end(self):
        return self.y + self.length
    @property
    def z_end(self):
        return self.z + self.height
    

    def shrink2D(self,  xmin: float, xmax: float, ymin: float, ymax: float) -> 'Rect3D':
        """
        Reduces the 2 dimensional size of the rect by the specified amounts. 
        xmin will reduce the size from the left side, xmax will reduce the size from the right side, and similar for the Y values. 
        """
        return Rect3D(
            z=self.z, height=self.height,  # unchanged
            x=self.x + xmin, width=self.width - xmin - xmax,
            y=self.y + ymin, length=self.length - ymin - ymax
        )
    def shrink2D_symmetrical(self, amount: float) -> 'Rect3D':
        """
        Will reduce the 2D size of the rect from all sides by the specified amount. 
        """
        return self.shrink2D(amount, amount, amount, amount)
    

    
    def to_numpy_array(self)-> NDArray[np.float64]:
        """
        Returns a numpy 2D array of the rect's bounds, namely:
        [
            [x_start, x_end],
            [y_start, y_end],
            [z_start, z_end]
        ]
        """
        return np.array(
            [
                [self.x, self.x_end],
                [self.y, self.y_end],
                [self.z, self.z_end]
            ]
        )
    
    def only_2d(self) -> Rect2D:
        """
        Get only the 2D component of this Rect3D
        """
        return Rect2D(
            x_start=self.x,
            x_end=self.x_end,
            y_start=self.y,
            y_end= self.y_end
        )



@dataclass
class Point3D:
    x: float
    y: float
    z: float

    def to_tuple(self) -> tuple[float, float, float]:
        return (self.x, self.y, self.z)




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

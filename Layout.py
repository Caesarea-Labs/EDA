from dataclasses import field, dataclass


@dataclass
class Point2D:
    x: int
    y: int

"""
A 2 dimensional shape, given by its edges. 
The order of edges is very important, as it determines how the sides are connected. Sides are connected from each edge to the next one.
"""
@dataclass
class Shape2D:
    edges: list[Point2D] = field(default_factory=list)

@dataclass
class Layout:
    layers: list[list[Shape2D]] = field(default_factory=list)




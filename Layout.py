from dataclasses import field, dataclass


@dataclass
class Point2D:
    x: int
    y: int

@dataclass
class Rect2D:
    x_start: int
    x_end: int
    y_start: int
    y_end: int

    def vertices(self) -> list[Point2D]:
        return [Point2D(self.x_start, self.y_start), Point2D(self.x_end, self.y_start), Point2D(self.x_end, self.y_end), Point2D(self.x_start, self.y_end)]

@dataclass
class MetalPolygon:
    """
    A 2 dimensional shape of a metal, given by its edges.
    The order of edges is very important, as it determines how the sides are connected. Sides are connected from each edge to the next one.
    """

    layer: int
    """
        The physically lowest metals have the smallest layer number.
    """
    vertices: list[Point2D]

@dataclass
class Via:
    """
    A connection between two metals on different layers, from bottomLayer to topLayer.
    A via has a physical shape, denoted by the rect propery.
    """
    bottomLayer: int
    topLayer: int
    rect: Rect2D


@dataclass
class Layout:
    """
        Layout of a chip, containing metals and connections (vias)
    """

    metals: list[MetalPolygon]
    """
        The physical metals, existing in integer layers
    """
    vias: list[Via]
    """
        Connections between metal layers.
    """



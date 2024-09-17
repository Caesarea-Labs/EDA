from dataclasses import dataclass
from typing import Optional, Iterator

from numpy import vecdot
from shapely import Polygon, STRtree

from utils import none_check


@dataclass
class Point2D:
    x: int
    y: int

    def __iter__(self) -> Iterator[int]:
        return iter((self.x, self.y))


@dataclass
class Point2DFloat:
    x: float
    y: float

    def __iter__(self) -> Iterator[float]:
        return iter((self.x, self.y))


@dataclass
class Rect2D:
    x_start: int
    x_end: int
    y_start: int
    y_end: int

    def vertices(self) -> list[Point2D]:
        """
        Returns the 4 vertices at the edges of the rectangle
        """
        return [Point2D(self.x_start, self.y_start), Point2D(self.x_end, self.y_start), Point2D(self.x_end, self.y_end),
                Point2D(self.x_start, self.y_end)]


class LayoutPolygon:

    layer: Optional[int]
    """
        The physical z height of the polygon. 
        Metals exist in this layer solely, while vias connect between this layer and the layer above it. 
    """
    gds_layer: Optional[int]
    """
        The relatively arbitrary layer value given to the polygon by the GDS file.
        Polygons with the same gds_layer are the same height, but a higher gds_layer value does not necessarily mean that the polygon is physically higher. 
    """

    # bottom_layer: int
    # top_layer: int
    vertices: list[Point2D]
    """
        The order of vertices is very important, as it determines how the sides are connected. Sides are connected from each vertex to the next one.
"""
    signal_index: Optional[int]
    name: str


@dataclass(eq = False)
class Metal(LayoutPolygon):
    """
    A 2 dimensional shape of a metal, given by its vertices.
    """

    vertices: list[Point2D]

    signal_index: Optional[int]
    """
    A number binding this metal and all metals connected to it. 
    When an electrical signal flow through a metal, the same signal flows through all metals with the same signal index.
    When the value is `None`, no signal has been assigned to the polygon, but it may be assigned a value by using signal_tracer.
    """
    name: str
    """String identifying the metal"""
    gds_layer: Optional[int] = None
    layer: Optional[int] = None

@dataclass
class Via(LayoutPolygon):
    """
       A connection between two metals on different layers, from bottomLayer to topLayer.
       A via has a physical shape, denoted by the rect propery.
       """

    # bottom_layer: int
    # top_layer: int
    rect: Rect2D
    name: str = "Via"
    gds_layer: Optional[int] = None
    layer: Optional[int] = None

    def __post_init__(self):
        self.vertices = self.rect.vertices()


@dataclass
class Layout:
    """
        Layout of a chip, containing metals and connections (vias)
    """

    metals: list[Metal]
    """
        The physical metals, existing in integer layers
    """
    vias: list[Via]
    """
        Connections between metal layers.
    """


    # def index_by_layer(self) -> list[list[Metal]]:
    #     """
    #     Returns a list of metals by layer. The first element is the first layer, second element is the second layer, etc.
    #     """
    #     layer_count = max(self.metals, key=lambda m: m.layer_2).layer + 1
    #     index = [[] for _ in range(layer_count)]
    #     for metal in self.metals:
    #         index[metal.layer].append(metal)
    #
    #     return index


MetalIndex = dict[int, STRtree]
def index_metals_by_gds_layer(layout: Layout) -> MetalIndex:
    """
    Returns a map of metals by gds_layer. 
    The layers are indexed in STRtrees for fast access
    """

    # Organize polygons by layer
    polygon_list_index: dict[int, list[Polygon]] = {}
    for metal in layout.metals:
        layer = none_check(metal.gds_layer)
        existing_list = polygon_list_index.get(layer, None)
        polygon = to_shapely_polygon(metal.vertices)
        if existing_list is None:
            # No polygons in layer - add a new list for layer
            polygon_list_index[layer] = [polygon]
        else:
            # Existing polygons in layer - add to list
            existing_list.append(polygon)

    # Optimize layers into STRtrees
    tree_index: dict[int, STRtree] = {layer: STRtree(polygons) for layer, polygons in polygon_list_index.items()}
    return tree_index



def to_shapely_polygon(vertices: list[Point2D]) -> Polygon:
    """
    Convert 2d points to a form supported by shapely
    """
    return Polygon([(x, y) for x, y in vertices])
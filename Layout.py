from dataclasses import dataclass
from typing import Optional, Iterator

from numpy import vecdot
from shapely import Polygon, STRtree

from geometry.geometry import Point2D, Polygon2D, Rect2D
from utils import max_of, none_check





# @dataclass
# class Point2DFloat:
#     x: float
#     y: float

#     def __iter__(self) -> Iterator[float]:
#         return iter((self.x, self.y))





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


@dataclass(eq=False)
class Metal(LayoutPolygon):
    """
    A 2 dimensional shape of a metal, given by its vertices.
    """

    polygon: Polygon2D

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
        self.vertices = self.rect.as_polygon()


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

    def layer_count(self) -> int:
        """
            Returns the highest layer of metals, plus 1
        """
        return max_of(self.metals, lambda m : none_check(m.layer)) + 1
    
    def max_signal(self) -> int:
        """
            Returns the highest layer of metals, plus 1
        """
        return max_of(self.metals, lambda m : none_check(m.layer)) + 1
    
    def metals_by_layer(self) -> list[list[Metal]]:
        layers = [[] for _ in range(len(self.metals))]
        for metal in self.metals:
            layers[none_check(metal.layer)].append(metal)
        
        return layers


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
        polygon = to_shapely_polygon(metal.polygon)
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

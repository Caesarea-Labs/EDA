from dataclasses import dataclass
from os import name
from typing import Optional, Iterator

from shapely import Polygon, STRtree

from eda.geometry.geometry_utils import to_shapely_polygon
from eda.geometry.polygon_triangulizer import AnnotatedMesh, ExtrudedPolygon, polygon_to_mesh
from eda.ui.plottable import Plottable

from .geometry.geometry import Point2D, Polygon2D, Rect2D
from .utils import max_of, min_of, none_check


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

    def with_layer(self, layer: int) -> 'Metal':
        return Metal(self.polygon, signal_index=self.signal_index, name=self.name, gds_layer=self.gds_layer, layer=layer)

    def __repr__(self) -> str:
        return f"{self.layer}:{represent_polygon(self.polygon)} #{self.signal_index} ({name})"


def represent_polygon(polygon: Polygon2D) -> str:
    if len(polygon) == 4:
        # quad
        min_x = min_of(polygon, lambda p: p.x)
        max_x = max_of(polygon, lambda p: p.x)
        min_y = min_of(polygon, lambda p: p.y)
        max_y = max_of(polygon, lambda p: p.y)

        width = (max_x - min_x)
        height = (max_y - min_y)

        # Check if they are close instead of equal because of potential floating point imprecision
        if abs(width - height) < 0.000001:
            # Square
            return f"Square[({min_x}, {min_y}), s={width}]"
        else:
            # Other quad
            return f"Quad[({min_x, min_y})->({max_x}, {max_y})]"
    else:
        return str([
            (float(point.x), float(point.y)) for point in polygon
        ])


@dataclass
class Via(LayoutPolygon):
    """
       A connection between two metals on different layers, from bottom_layer to top_layer.
       A via has a physical shape, denoted by the rect propery.
       """

    rect: Rect2D
    name: str = "Via"
    gds_layer: Optional[int] = None
    """
    Assigned when a via is loaded from a GDS file, but not necessary for plotting and final algorithms.
    """
    bottom_layer: Optional[int] = None
    """
    The bottom-most Z value of the via, usually 1 less than the top_layer. 
    Assigned with inflate_layout and required for most applications. 
    """
    top_layer: Optional[int] = None
    """
    The top-most Z value of the via, usually 1 more than the bottom_layer. 
    Assigned with inflate_layout and required for most applications. 
    """
    mark: bool = False
    """
    If true, will be specially marked when plotted out
    """

    def with_layers(self, bottom: int, top: int) -> 'Via':
        return Via(rect=self.rect, name=self.name, gds_layer=self.gds_layer, mark=self.mark, bottom_layer=bottom, top_layer=top)

    def __post_init__(self):
        self.vertices = self.rect.as_polygon()


@dataclass
class Layout(Plottable):
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
        return max_of(self.metals, lambda m: none_check(m.layer)) + 1

    def max_signal(self) -> int:
        """
            Returns the highest layer of metals, plus 1
        """
        return max_of(self.metals, lambda m: none_check(m.layer)) + 1

    def metals_by_layer(self) -> list[list[Metal]]:
        layers = [[] for _ in range(len(self.metals))]
        for metal in self.metals:
            layers[none_check(metal.layer)].append(metal)

        return layers

    def with_added_vias(self, vias: list[Via]) -> 'Layout':
        return Layout(self.metals, self.vias + vias)
    
    def to_meshes(self) -> list[AnnotatedMesh]:
        fill_colors = ['cyan', 'lightgreen', 'lightblue', 'orange', 'yellow',
               'pink', 'lightcoral', 'lightgray', 'lavender', 'beige']
        
        meshes = []

        for via in self.vias:
            meshes.append(via_to_mesh(via, "black", "vias"))

        for metal in self.metals:
            polygon = ExtrudedPolygon(
                z_base=none_check(metal.layer) - 0.25,
                z_top=none_check(metal.layer) + 0.25,
                color=fill_colors[none_check(metal.signal_index) % len(fill_colors)],
                # edge_color=edge_colors[metal.signal_index % len(edge_colors)],
                vertices=metal.polygon,
                alpha=0.5,
                name=metal.name,
                group_name=str(metal.signal_index)
            )
            meshes.append(polygon_to_mesh(polygon))

        return meshes
    
def via_to_mesh(via: Via, color: str, group_name: str)-> AnnotatedMesh:
    polygon = ExtrudedPolygon(
        z_base=none_check(via.bottom_layer),
        z_top=none_check(via.top_layer, f"Missing top_layer value for via (bottom_layer is specified: {via.bottom_layer})"),
        color=color,
        vertices=via.rect.as_polygon(),
        alpha=0.3,
        name=via.name,
        group_name=group_name
    )
    return polygon_to_mesh(polygon)

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



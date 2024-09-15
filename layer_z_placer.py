from typing import Tuple

from shapely import STRtree, Polygon

from Layout import Layout
from utils import none_check


def layer_layout(layout: Layout):
    """
    Reassigns the `layer` value in the `LayoutPolygon`s of the layout.
    It does this by considering the initial `gds_layer` value of the `LayoutPolygon`s, and by checking which vias exist at metal intersections.
    If a via layer often exists in an intersection of 2 specific metal layers, we deduce that it physically exists between them.
    If there's a place where a via exists but one of 2 layers don't, that means that via layer cannot be connecting between them.
    """

    indexed = index_by_gds_layer(layout)
    pass


def index_by_gds_layer(layout: Layout) -> list[STRtree]:
    """
    Returns a list of metals by gds_layer. The first element is the first layer, second element is the second layer, etc.
    The layers are indexed in STRtrees for fast access
    """
    layer_count = none_check(max(layout.metals, key=lambda m: none_check(m.gds_layer)).gds_layer) + 1
    # Organize polygons by layer
    polygon_list_index: list[list[Polygon]] = [[] for _ in range(layer_count)]
    for metal in layout.metals:
        vertex_pairs: list[Tuple[int, int]] = [(x, y) for x, y in metal.vertices]
        polygon_list_index[none_check(metal.gds_layer)].append(Polygon(vertex_pairs))

    # Optimize layers into STRtrees
    tree_index: list[STRtree] = [STRtree(polygons) for polygons in polygon_list_index]

    return tree_index

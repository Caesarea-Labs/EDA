from ast import main
from curses import meta
from dataclasses import dataclass
from operator import pos
from typing import Tuple
from xmlrpc.client import Boolean

from cycler import V
from shapely import STRtree, Polygon

from Layout import Layout, Point2D, Rect2D, Via
from Shapes import lamed_shape, rect_shape
from utils import none_check

MetalIndex = dict[int, STRtree]
ViaIndex = dict[int, list[Via]]

# TODO: The two metal edges are the one with only one via connecting them. To decide which one is on top, use the one with the higher gds_layer value.


def layer_layout(layout: Layout):
    """
    Reassigns the `layer` value in the `LayoutPolygon`s of the layout
    It does this by considering the initial `gds_layer` value of the `LayoutPolygon`s, and by checking which vias exist at metal intersections.
    If a via layer often exists in an intersection of 2 specific metal layers, we deduce that it physically exists between them.
    If there's a place where a via exists but one of 2 layers don't, that means that via layer cannot be connecting between them.
    """

    indexed = index_metals_by_gds_layer(layout)
    via_layers = index_vias_by_gds_layer(layout)
    via_to_metal_layers: dict[int, Tuple[int, int]] = {
        # Assign connect metals for each via layer
        none_check(via_layer): get_via_layer_connected_metal_layers(via_layer, vias, indexed) for via_layer, vias in via_layers.items()
    }
    x = 2
    # TODO: just need to test now
    pass


def get_via_layer_connected_metal_layers(via_layer: int, vias: list[Via], index: MetalIndex) -> Tuple[int, int]:
    """Returns the two gds_layers that this via layer is connected to, by filtering through metal layers that actually have metals in the via points."""
    # Only get metals that actually connect to all vias, which implies those metals are above/below the via. 
    possible_metal_layers = [layer for layer in index.keys() if all_vias_touch_metals(vias, index[layer])]
    
    assert len(possible_metal_layers) <= 2, f"More than two possible metal layers could be connected to via layer {via_layer}: {possible_metal_layers}"
    assert len(possible_metal_layers) >= 2, f"Cannot find two metal layers that match via connections of layer {via_layer}, only found that {possible_metal_layers} matches"
    
    return (possible_metal_layers[0], possible_metal_layers[1])



def all_vias_touch_metals(vias: list[Via], metals: STRtree) -> bool:
    return all(via_touches_any_metal(via, metals) for via in vias)

def via_touches_any_metal(via: Via, metals: STRtree) -> bool:
    as_polygon = to_shapely_polygon(via.vertices)
    # This step is very important as it vastly reduces the amount of intersection checks we need to do, essentially making this operation O(1) instead of O(n)
    candidates = metals.query(as_polygon)
    return any(candidate.intersects(as_polygon) for candidate in candidates)


def index_vias_by_gds_layer(layout: Layout) -> ViaIndex:
    """
    Returns a map of vias by gds_layer. 
    """

    # Organize polygons by layer
    via_index: dict[int, list[Via]] = {}
    for via in layout.vias:
        # Convert 2d points to a form supported by shapely
        layer = none_check(via.gds_layer)
        existing_list = via_index.get(layer, None)
        if existing_list is None:
            # No polygons in layer - add a new list for layer
            via_index[layer] = [via]
        else:
            # Existing polygons in layer - add to list
            existing_list.append(via)

    # Optimize layers into STRtrees
    return via_index


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


if __name__ == "__main__":
    shape = lamed_shape(1, 3, 2, 2)
    test_layout = Layout(metals=[
        shape.named("A").metal(gds_layer=10),
        shape.named("B").translate(6, 5).metal(gds_layer=10),

        shape.named("C").translate(1, 1).metal(gds_layer=11),
        shape.named("D").translate(8, 6).metal(gds_layer=11),

        shape.named("E").translate(0, 6).metal(gds_layer=12),
        lamed_shape(1, 5, 2, 2, name="F").rotate(270).mirror_vertical().translate(8, 2).metal(gds_layer=12),

        lamed_shape(1, 4, 2, 2, name="G").translate(0, 3).metal(gds_layer=13),
        shape.named("H").translate(8, 7).metal(gds_layer=13),

        shape.named("I").translate(4, 4).metal(gds_layer=14),

        rect_shape(width=2, height=1, name="d_int").translate(10, 10).metal(gds_layer=12),

        rect_shape(width=1, height=1, name="b_int1").translate(6, 8).metal(gds_layer=11),
        rect_shape(width=1, height=1, name="b_int2").translate(6, 8).metal(gds_layer=12),
        rect_shape(width=1, height=1, name="b_int3").translate(6, 8).metal(gds_layer=13),

        rect_shape(width=1, height=1, name="c_int1").translate(4, 5).metal(gds_layer=12),
        rect_shape(width=1, height=1, name="c_int2").translate(4, 5).metal(gds_layer=13),
    ],
        vias=[
            Via(
                gds_layer=20,
                rect=Rect2D(x_start=3, x_end=5, y_start=4, y_end=6),
                name="a"
            ),
            Via(
                gds_layer=20,
                rect=Rect2D(x_start=6, x_end=7, y_start=8, y_end=9),
                name="b1"
            ),
            Via(
                gds_layer=21,
                rect=Rect2D(x_start=6, x_end=7, y_start=8, y_end=9),
                name="b2"
            ),
            Via(
                gds_layer=22,
                rect=Rect2D(x_start=6, x_end=7, y_start=8, y_end=9),
                name="b3"
            ),
            Via(
                gds_layer=23,
                rect=Rect2D(x_start=6, x_end=7, y_start=8, y_end=9),
                name="b4"
            ),
            Via(
                gds_layer=21,
                rect=Rect2D(x_start=4, x_end=5, y_start=5, y_end=6),
                name="c1"
            ),
            Via(
                gds_layer=22,
                rect=Rect2D(x_start=4, x_end=5, y_start=5, y_end=6),
                name="c2"
            ),
            Via(
                gds_layer=23,
                rect=Rect2D(x_start=4, x_end=5, y_start=5, y_end=6),
                name="c3"
            ),
            Via(
                gds_layer=21,
                rect=Rect2D(x_start=10, x_end=12, y_start=10, y_end=11),
                name="d1"
            ),
            Via(
                gds_layer=22,
                rect=Rect2D(x_start=10, x_end=12, y_start=10, y_end=11),
                name="d2"
            ),
            Via(
                gds_layer=22,
                rect=Rect2D(x_start=1, x_end=2, y_start=6, y_end=8),
                name="e"
            ),
            Via(
                gds_layer=22,
                rect=Rect2D(x_start=1, x_end=2, y_start=3, y_end=4),
                name="f"
            )
    ]
    )

    layer_layout(test_layout)


def to_shapely_polygon(vertices: list[Point2D]) -> Polygon:
    """
    Convert 2d points to a form supported by shapely
    """
    return Polygon([(x,y) for x,y in vertices])
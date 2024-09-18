from dataclasses import replace
from typing import Tuple

from shapely import STRtree, Polygon

from Draw import plot_layout
from Layout import Layout, Metal, MetalIndex, Point2D, Via, index_metals_by_gds_layer, to_shapely_polygon
from test_layout import test_layout_const
from utils import none_check

ViaIndex = dict[int, list[Via]]


def scrambled_test_layout() -> Layout:
    """
    test layout converted to "hard mode", with no proper information on layers, but with less-reliable gds_layer information.
    """
    new_metals = [Metal(vertices=metal.vertices, layer=None, signal_index=metal.signal_index, name=metal.name,
                        gds_layer=none_check(metal.layer) + 10) for metal in test_layout_const.metals]
    new_vias = [Via(
                gds_layer=none_check(via.layer) + 20,
                layer=None,
                rect=via.rect,
                name=via.name
                ) for via in test_layout_const.vias]
    return Layout(new_metals, new_vias)




# TODO: The two metal edges are the one with only one via connecting them. To decide which one is on top, use the one with the higher gds_layer value.


def inflate_layout(layout: Layout) -> Layout:
    """
    Returns a new layout, with the `layer` value reassigned in the `LayoutPolygon`s of the layout
    It does this by considering the initial `gds_layer` value of the `LayoutPolygon`s, and by checking which vias exist at metal intersections.
    If a via layer often exists in an intersection of 2 specific metal layers, we deduce that it physically exists between them.
    If there's a place where a via exists but one of 2 layers don't, that means that via layer cannot be connecting between them.
    """

    indexed = index_metals_by_gds_layer(layout)
    via_layers = index_vias_by_gds_layer(layout)
    via_to_metal_layers: dict[int, tuple[int, int]] = {
        # Assign connect metals for each via layer
        none_check(via_layer): get_via_layer_connected_metal_layers(via_layer, vias, indexed) for via_layer, vias in via_layers.items()
    }
    metal_gds_layer_to_layer, via_gds_layer_to_layer = order_layers(via_to_metal_layers)

    new_metals = [replace(metal, layer=metal_gds_layer_to_layer[none_check(metal.gds_layer)]) for metal in layout.metals]
    new_vias = [replace(via, layer=via_gds_layer_to_layer[none_check(via.gds_layer)]) for via in layout.vias]

    return Layout(new_metals, new_vias)


def order_layers(via_to_metal_layers: dict[int, tuple[int, int]]) -> tuple[dict[int, int], dict[int, int]]:
    """
    Returns a map from the METAL gds_layers to the actual 0-indexed layers, and from the VIA gds_layers to the actual 0-indexed layers.
    """
    # 1. Find out where the start and end are
    current = find_lowest_layer(via_to_metal_layers)

    # 2. Graph like, start from the start as index 0, and treat the metal it is connected to as index i+1.
    # This dict maps every metal layer to the connected metal layer AND the connecting via gds_layer
    metal_connections: dict[int, tuple[int, int]] = {
        start: (end, via) for via, (start, end) in via_to_metal_layers.items()}
    metal_gds_layer_to_layer: dict[int, int] = {}
    via_gds_layer_to_layer: dict[int, int] = {}
    layer_index = 0
    while current in metal_connections:
        # Assign the same layer to the start metal and the connecting via
        end_metal, via = metal_connections[current]
        metal_gds_layer_to_layer[current] = layer_index
        via_gds_layer_to_layer[via] = layer_index

        # Travel further in the 'graph'
        layer_index += 1
        current = end_metal

    # Add the highest layer mapping, since the loop stops before running on the last element.
    metal_gds_layer_to_layer[current] = layer_index

    assert len(metal_gds_layer_to_layer) == len(via_to_metal_layers) + \
        1, f"There isn't a proper layer mapping for every gds_layer (expected {len(via_to_metal_layers) + 1}, got {len(metal_gds_layer_to_layer)})"

    return metal_gds_layer_to_layer, via_gds_layer_to_layer


def find_lowest_layer(via_to_metal_layers: dict[int, tuple[int, int]]) -> int:
    # Metal layer is connected to one via layer - it's a start or end.
    # Metal layer is connected to two via layers - it's a middle point
    # Metal layer is connected to more than two via layers - that's a contradication, throw an error.
    connection_count: dict[int, int] = {}

    # Count connections to vias
    for start, end in via_to_metal_layers.values():
        connection_count[start] = connection_count.get(start, 0) + 1
        connection_count[end] = connection_count.get(end, 0) + 1

    for layer, connections in connection_count.items():
        assert connections <= 2, f"The metal layer {layer} seems to be connected to {connections} via layers, but physically it can only be connected to up to two."

    # Metal layer is connected to one via layer - it's a start or end.
    edges = {layer: count for layer, count in connection_count.items() if count == 1}

    edge_count = len(edges)
    assert edge_count != 0, "Cannot find any metal layers connected to exactly one via layer, to serve as the edge layers."
    assert edge_count != 1, f"Could only find one metal layer ({edges[0]}) to serve as an edge, but two are expected."
    assert edge_count == 2, f"Too many metal layers ({edge_count} instead of 2) connect to exactly one via layers, making them potential edge layers: {edges}"

    # By calling min(), we implicitly decide that a lower gds_layer means that it is the lowest layer, and a higher gds_layer means it is the highest layer.
    return min(edges.keys())


def get_via_layer_connected_metal_layers(via_layer: int, vias: list[Via], index: MetalIndex) -> tuple[int, int]:
    """Returns the two gds_layers that this via layer is connected to, by filtering through metal layers that actually have metals in the via points."""
    # Only get metals that actually connect to all vias, which implies those metals are above/below the via.
    possible_metal_layers = [layer for layer in index.keys() if all_vias_touch_metals(vias, index[layer])]

    assert len(possible_metal_layers) <= 2, f"More than two possible metal layers could be connected to via layer {via_layer}: {possible_metal_layers}.\
 All of the vias on that level hit metals in all layers equally ({len(vias)} times)."
    assert len(
        possible_metal_layers) != 1, f"Cannot find two metal layers that match via connections of layer {via_layer}, only found that layer {possible_metal_layers[0]} matches."
    assert len(
        possible_metal_layers) != 0, f"Cannot find any metal layers that match via connections of layer {via_layer}."

    return (possible_metal_layers[0], possible_metal_layers[1])


def all_vias_touch_metals(vias: list[Via], metals: STRtree) -> bool:
    return all(via_touches_any_metal(via, metals) for via in vias)


def via_touches_any_metal(via: Via, metals: STRtree) -> bool:
    as_polygon = to_shapely_polygon(via.vertices)
    # This step is very important as it vastly reduces the amount of intersection checks we need to do, essentially making this operation O(1) instead of O(n)
    candidates = metals.query(as_polygon)
    print(f"Candidates = {candidates}")
    print(f"Intersecting Candidates = {[candidate for candidate in candidates if as_polygon.intersects(metals.geometries[candidate])]}")

    return any(as_polygon.intersects(metals.geometries[candidate]) for candidate in candidates)


def index_vias_by_gds_layer(layout: Layout) -> ViaIndex:
    """
    Returns a map of vias by gds_layer. 
    """

    # Organize polygons by layer
    via_index: dict[int, list[Via]] = {}
    for via in layout.vias:
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





if __name__ == "__main__":
    inflated = inflate_layout(scrambled_test_layout())
    plot_layout(inflated, 18, 5)


from dataclasses import dataclass
import itertools
from typing import Iterable, Optional

from shapely import STRtree
from eda.geometry.geometry_utils import to_shapely_polygon
from eda.layout import Layout, Via, MetalIndex, index_metals_by_gds_layer
from eda.layout_inflation import GdsLayerMapping, index_vias_by_gds_layer
from eda.utils import none_check


@dataclass
class ViaLayerConnections:
    close_start: int
    """
    A layer that is 1 physical layer below the end.
    """
    far_start: Optional[int]
    """
    Possible second layer this via layer is connected to, with a distance of 2 layers from the end.
    """
    end: int

    def all_connections(self) -> list[int]:
        if self.far_start is None:
            return [self.close_start, self.end]
        else:
            return [self.close_start, self.far_start, self.end]
        

def map_layers(layout: Layout) -> GdsLayerMapping:
    """
    It does this by considering the initial `gds_layer` value of the `LayoutPolygon`s, and by checking which vias exist at metal intersections.
    If a via layer often exists in an intersection of 2 specific metal layers, we deduce that it physically exists between them.
    If there's a place where a via exists but one of 2 layers don't, that means that via layer cannot be connecting between them.
    """
    metal_index = index_metals_by_gds_layer(layout)
    via_layers = index_vias_by_gds_layer(layout)
    via_to_metal_layers: dict[int, ViaLayerConnections] = {
        # Assign connected metals for each via layer
        none_check(via_layer): get_via_layer_connected_metal_layers(via_layer, vias, metal_index) for via_layer, vias in via_layers.items()
    }
    metal_gds_layer_with_mappings = {metal_gds_layer for connections in via_to_metal_layers.values()
                                     for metal_gds_layer in connections.all_connections()}
    actual_gds_metal_layers = metal_index.keys()

    assert metal_gds_layer_with_mappings == actual_gds_metal_layers, \
        f"Could not find the via layers that connect to every metal layer. \
    This can happen if double-length via layers are ambigous in what are the two metal layers they connect to.\
    All metal layers: {set(actual_gds_metal_layers)}. Metal layers with mappings: {metal_gds_layer_with_mappings} "

    order_result = order_layers(via_to_metal_layers)
        
def order_layers(via_to_metal_layers: dict[int, ViaLayerConnections]) -> GdsLayerMapping:
    """
    Returns a map from the METAL gds_layers to the actual 0-indexed layers,
    and from the VIA gds_layers to the actual 0-indexed layers, the via ends at (the top part).
    :param via_to_metal_layers A map calculated in the previous step, that assigns every via the metal layers it is connected to.
    """
    # 1. Find out where the start and end are
    current = find_highest_layer(via_to_metal_layers)

    # 2. Graph like, start from the highest layer at index n-1, and go down finding metals below it by following via connections.
    metal_connections: dict[int, ConnectionEnd] = {
        connections.end: ConnectionEnd(
            via_gds_layer=via, metal_start_gds_layer_close=connections.close_start, metal_start_gds_layer_far=connections.far_start
        ) for via, connections in via_to_metal_layers.items()
    }

    metal_gds_layer_to_layer: dict[int, int] = {}
    via_gds_layer_to_layer: dict[int, ViaLayerConnections] = {}
    layer_count = count_layers(metal_connections.values())
    # Start from the ending index
    layer_index = layer_count - 1
    while current in metal_connections:
        connection_end = metal_connections[current]
        # The top layer index is assigned to the metal
        metal_gds_layer_to_layer[current] = layer_index

        if connection_end.metal_start_gds_layer_far is not None:
            # Case 1: This is a double via layer. We need to assign a layer to the close metal layer and skip two layers down.

            # Assign layer to close metal layer
            metal_gds_layer_to_layer[connection_end.metal_start_gds_layer_close] = layer_index - 1

            # Associate the via gds_layer with the physical via layers it is associated it.
            # Obviously, it will just be consecutive indices.
            via_gds_layer_to_layer[connection_end.via_gds_layer] = ViaLayerConnections(
                close_start=layer_index - 1,
                far_start=layer_index-2,
                end=layer_index
            )

            # Mark we are going two layers down, traveling through the graph
            layer_index -= 2
            current = connection_end.metal_start_gds_layer_far
        else:
            # Case 2: This is a single-layer via

            # Associate the via gds_layer with the physical via layers it is associated it.
            # This time there is no 'far start' because it's just one layer this via layer is spanning.
            via_gds_layer_to_layer[connection_end.via_gds_layer] = ViaLayerConnections(
                close_start=layer_index - 1,
                far_start=None,
                end=layer_index
            )

            # Mark we are going one layer down, traveling through the graph
            layer_index -= 1
            current = connection_end.metal_start_gds_layer_close

    assert layer_index == 0, f"Didn't end at the bottom index 0, instead ended at {layer_index}."

    # Add the highest layer mapping, since the loop stops before running on the last element.
    metal_gds_layer_to_layer[current] = layer_index

    gds_layer_mapping_count = len(metal_gds_layer_to_layer)
    # count_layers = len(via_to_metal_layers) + 1
    if gds_layer_mapping_count != layer_count:
        all_metal_gds_layers = {metal_layer for connection in via_to_metal_layers.values() for metal_layer in connection.all_connections()}
        missing_mappings = [layer for layer in all_metal_gds_layers if layer not in metal_gds_layer_to_layer]
        assert False, (f"There isn't a proper layer mapping for every gds_layer (expected {count_layers}, got {gds_layer_mapping_count})."
                       f"Layers without mappings: {missing_mappings}. All mappings: {metal_gds_layer_to_layer}.")

    return OrderLayersResult(metal_gds_layer_to_layer, via_gds_layer_to_layer)




def find_highest_layer(via_to_metal_layers: dict[int, ViaLayerConnections]) -> int:
    # Metal layer is connected to one via layer - it's a start or end.
    # Metal layer is connected to two via layers - it's a middle point
    # Metal layer is connected to more than two via layers - that's a contradication, throw an error.
    connection_count: dict[int, int] = {}

    # Count connections to vias
    for connections in via_to_metal_layers.values():
        start_a = connections.close_start
        start_b = connections.far_start
        end = connections.end
        connection_count[start_a] = connection_count.get(start_a, 0) + 1
        if start_b != None:
            connection_count[start_b] = connection_count.get(start_b, 0) + 1
        connection_count[end] = connection_count.get(end, 0) + 1

    for layer, connections in connection_count.items():
        assert connections <= 2, f"The metal layer {layer} seems to be connected to {connections} Via layers, but physically it can only be connected to up to two."

    # Metal layer is connected to one via layer - it's a start or end.
    edges = {layer: count for layer, count in connection_count.items() if count == 1}

    edge_count = len(edges)
    assert edge_count != 0, "Cannot find any metal layers connected to exactly one via layer, to serve as the edge layers."
    assert edge_count != 1, f"Could only find one metal layer ({edges[0]}) to serve as an edge, but two are expected."
    assert edge_count <= 3, f"Too many metal layers ({edge_count} instead of 2 or 3) connect to exactly one via layer, making them potential edge layers: {edges}"

    # By calling max(), we implicitly decide that a lower gds_layer means that it is the lowest layer, and a higher gds_layer means it is the highest layer.
    return max(edges.keys())


def get_via_layer_connected_metal_layers(via_layer: int, vias: list[Via], index: MetalIndex) -> ViaLayerConnections:
    """Returns the two gds_layers that this via layer is connected to, by filtering through metal layers that actually have metals in the via points."""
    # Only get metals that actually connect to all vias, which implies those metals are above/below the via.
    possible_metal_layers = sorted([layer for layer in index.keys() if all_vias_touch_metals(vias, index[layer])])

    if len(possible_metal_layers) == 2:
        # Case 1: The simple case. The via layer connects a single metal layer to a single metal layer above it.
        # In this case all vias must touch a metal in both layers.
        return ViaLayerConnections(close_start=possible_metal_layers[0], end=possible_metal_layers[1], far_start=None)
    elif len(possible_metal_layers) == 1:
        top_layer = possible_metal_layers[0]
        # Case 2: The via layer connects up to a single upper layer, and connects down to two different metal layers below it.
        # This can happen when the lower layer is diffusion, and in that case extra long vias are sometimes connected from the diffusion
        # To a metal layer 2 layers above it.
        other_layers = [layer for layer in index.keys() if layer != top_layer]
        other_pairs = itertools.combinations(other_layers, 2)
        # Try to fit all pairs of layers as the pair that is connected to the bottom of this via layer
        matching_layer_pairs = [pair for pair in other_pairs if all_vias_touch_metals_in_either(vias, index[pair[0]], index[pair[1]])]
        assert len(
            matching_layer_pairs) == 1, f"Expected only one pair to match as the bottom layer connected to layer {top_layer} with via {via_layer}, got: {matching_layer_pairs}"
        # By sorting like this, we imply if the layer number is far from the top layer number, then it is physically farther away.
        close_start, far_start = sorted(list(matching_layer_pairs[0]), key=lambda layer: abs(top_layer - layer))
        return ViaLayerConnections(
            close_start=close_start,
            far_start=far_start,
            end=top_layer
        )
    else:
        if len(possible_metal_layers) > 2:
            raise AssertionError(f"More than two possible metal layers could be connected to via layer {via_layer}: {possible_metal_layers}.\
        All of the vias on that level hit metals in all layers equally ({len(vias)} times).")
        else:
            raise AssertionError(f"Cannot find any metal layers that match via connections of layer {via_layer}.")

@dataclass
class ConnectionEnd:
    via_gds_layer: int
    metal_start_gds_layer_close: int
    metal_start_gds_layer_far: Optional[int]


def count_layers(connections: Iterable[ConnectionEnd]) -> int:
    """
    Count how many total layers we have to set the max index. 
    if we have 'double layers' with a metal_start_gds_layer_far value set, they will span 2 layers so we need to take that into account. 
    """
    layers = 0
    for connection in connections:
        if connection.metal_start_gds_layer_far is None:
            layers += 1
        else:
            layers += 2
    return layers



def all_vias_touch_metals(vias: list[Via], metals: STRtree) -> bool:
    return all(via_touches_any_metal(via, metals) for via in vias)


def via_touches_any_metal(via: Via, metals: STRtree) -> bool:
    as_polygon = to_shapely_polygon(via.vertices)
    # This step is very important as it vastly reduces the amount of intersection checks we need to do, essentially making this operation O(1) instead of O(n)
    candidates = metals.query(as_polygon)

    return any(as_polygon.intersects(metals.geometries[candidate]) for candidate in candidates)

def all_vias_touch_metals_in_either(vias: list[Via], metalsA: STRtree, metalsB: STRtree) -> bool:
    """
    Checks if all vias in the list touch a metal in either STRtree of metals.
    """
    return all(via_touches_any_metal(via, metalsA) or via_touches_any_metal(via, metalsB) for via in vias)

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


import array
from dataclasses import dataclass, replace
import itertools
from typing import Iterable, Optional, Tuple, cast

from shapely import STRtree, Polygon

from eda.geometry.geometry_utils import PolygonIndex

from .layout import Layout, Metal, MetalIndex, Via, index_metals_by_gds_layer, to_shapely_polygon
# from .plotly_layout import plotly_plot_layout
from .utils import none_check, sum_of

ViaIndex = dict[int, list[Via]]


@dataclass
class ViaLayerMapping:
    bottom_metal_index: int
    """
    The metal layer the longest vias in the layer start at. Usually top_metal_index-1. 
    """
    top_metal_index: int
    """
    The metal layer all vias end at. 
    """


@dataclass
class GdsLayerMapping:
    metal_gds_layer_order: list[list[int]]
    """
    The first value is all gds_layers mapped to the first physical layer, the second one is all above it, and so on. 
    """
    via_gds_layer_connections: dict[int, ViaLayerMapping]
    """
    A map from each gds via layer to the vertical range that its vias span.  
    """

@dataclass
class ViaLayer:
    gds_layer: int
    double: bool
    """
    If true, the via will be considered a double via that connects 3 layers of metals. 
    """

def build_gds_layer_mapping(metal_gds_layer_order: list[int | list[int]], via_gds_layers: list[int | list[int]]) -> GdsLayerMapping:
    """
    Utility method for constructing a GdsLayerMapping.
    metal_gds_layer_order will interpret single values as a list with that element as the only element.
    via_layers will interpret each element as a seperate via gds_layer, with the bottom metal layer of the via being equal to the index.
    If a list is provided instead of a single element, the via will be considered a double via that connects 3 layers of metals. 
    """
    via_mapping: dict[int, ViaLayerMapping] = {}
    metal_index = 0
    for via_gds_layer in via_gds_layers:
        if isinstance(via_gds_layer, int):
            via_mapping[via_gds_layer] = ViaLayerMapping(bottom_metal_index=metal_index, top_metal_index=metal_index + 1)
            metal_index += 1
        else:
            actual_gds_layer =  via_gds_layer[0]
            via_mapping[actual_gds_layer] = ViaLayerMapping(bottom_metal_index=metal_index, top_metal_index=metal_index + 2)
            metal_index += 2
    metals_as_list = [[layers] if isinstance(layers, int) else layers for layers in  metal_gds_layer_order]
    return GdsLayerMapping(metals_as_list, via_mapping)


# @dataclass
# class OrderLayersResult:
#     metal_gds_layer_to_layer: dict[int, int]
#     """
#     A map from a metal gds_layer to an actual 0-indexed physical 3D metal layer. 
#     """
#     via_gds_layer_connections: dict[int, ViaLayerConnections]
#     """
#     A map from a via gds_layer to the actual 0-indexed physical 3D bottom and top layers that a via is connected to. 
#     """


def inflate_layout(layout: Layout, layer_mapping: GdsLayerMapping) -> Layout:
    """
    Returns a new layout, with the `layer` value reassigned in the `LayoutPolygon`s of the layout
    """

    # Map gds layers to their index
    gds_layer_to_index: dict[int, int] = {}
    for index, gds_layers in enumerate(layer_mapping.metal_gds_layer_order):
        for gds_layer in gds_layers:
            gds_layer_to_index[gds_layer] = index

    new_metals = [inflate_metal(metal, gds_layer_to_index) for metal in layout.metals]
    metal_index = index_metals_by_layer(new_metals)
    new_vias = [inflate_via(via, layer_mapping.via_gds_layer_connections, metal_index) for via in layout.vias]

    return Layout(new_metals, new_vias)


def inflate_metal(metal: Metal, metal_gds_layer_to_layer: dict[int, int]) -> Metal:
    gds_layer = none_check(metal.gds_layer)

    assert gds_layer in metal_gds_layer_to_layer, f"There was no gds layer mapping for the metal gds layer {gds_layer}. Available mappings: {set(metal_gds_layer_to_layer.keys())}"
    return metal.with_layer(metal_gds_layer_to_layer[gds_layer])


def inflate_via(via: Via, via_gds_layer_connections:  dict[int, ViaLayerMapping], metal_index: MetalIndex) -> Via:
    connections = via_gds_layer_connections[none_check(via.gds_layer)]
    top_layer = connections.top_metal_index
    bottom_layer = get_via_bottom_connection_layer(via, connections, metal_index)
    return via.with_layers(bottom=bottom_layer, top=top_layer)


def get_via_bottom_connection_layer(via: Via, connections: ViaLayerMapping, metal_index: MetalIndex) -> int:
    if connections.bottom_metal_index == connections.top_metal_index - 1:
        # Simple case: The via layer only spans one layer, so the bottom connection must be one layer below it.
        return connections.bottom_metal_index
    else:
        # Complex case: The via gds layer spans two layers so this specific via can be connected to any of the metals below it.

        # See if the via hits a metal in the highest layer, then travel further down.
        for lower_layer in range(connections.top_metal_index - 1, connections.bottom_metal_index - 1, -1):
            metals = metal_index[lower_layer]
            if via_intersects(via, metals):
                return lower_layer
        
        raise AssertionError(f"Could not find any metal that the via {via} is supposed to hit between layers {connections.top_metal_index - 1} and {connections.bottom_metal_index}")
        # # Choose the one that the via intersects MORE with.
        # close_metals = metal_index[connections.bottom_metal_index]
        # far_metals = metal_index[connections.far_start]
        # close_intersection = via_intersection_area(via, close_metals)
        # far_intersection = via_intersection_area(via, far_metals)

        # assert close_intersection > 0 or far_intersection > 0, f"According to previous analysis, the via {via} should be connected to either metal layer {connections.close_start} or {connections.far_start}, but it seems to be connected to none of them."

        # if close_intersection > far_intersection:
        #     return connections.close_start
        # else:
        #     return connections.far_start


# def via_intersection_area(via: Via, metals: STRtree) -> float:
#     as_polygon = to_shapely_polygon(via.vertices)
#     # This step is very important as it vastly reduces the amount of intersection checks we need to do, essentially making this operation O(1) instead of O(n)
#     candidates = metals.query(as_polygon)
#     intersections = [as_polygon.intersection(cast(Polygon, metals.geometries[candidate])) for candidate in candidates]
#     return sum_of(intersections, key=lambda intersection: intersection.area)

def via_intersects(via: Via, metals: STRtree) -> bool:
    as_polygon = to_shapely_polygon(via.vertices)
    # This step is very important as it vastly reduces the amount of intersection checks we need to do, essentially making this operation O(1) instead of O(n)
    candidates = metals.query(as_polygon)
    return any([as_polygon.intersects(cast(Polygon, metals.geometries[candidate])) for candidate in candidates])



# MetalIndex = dict[int, STRtree]

def index_metals_by_layer(metals: list[Metal]) -> MetalIndex:
    """
    Returns a map of metals by gds_layer. 
    The layers are indexed in STRtrees for fast access
    """

    # Organize polygons by layer
    polygon_list_index: dict[int, list[Polygon]] = {}
    for metal in metals:
        layer = none_check(metal.layer)
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



import copy
from itertools import combinations
from typing import Iterable, Tuple, cast
from networkx import Graph, connected_components
from shapely import Polygon, STRtree

from .layout import Layout, Metal, Point2D, Via
from .plotly_layout import plotly_plot_layout
from .test_layout import test_layout_const
from .utils import max_of, none_check


def trace_signals(layout: Layout) -> Layout:
    """Will return a new layout with the MetalPolygons having the signal_index value set, to match how the metals and vias connect to each other. 
    This requires having the layer field set."""

    new_layout = copy.deepcopy(layout)
    # The signals tracing problem can be easily converted to the problem of connected components in an undirected graph.
    # A 'signal' is essentially a connected component in a graph where the nodes are metals, and edges are physical connections between metals.
    # These physical connections boil down to a via connected to two or more metals, each link between pairs of metals producing at least one edge.
    # In the future, we will also consider intersections or exact adjacency of metals as links/edges between models.
    signal_graph = signals_to_graph(new_layout)

    components = cast(Iterable[set[Metal]], connected_components(signal_graph))

    # The signal index is just the index of the connected component of the metals
    for signal_index, component in enumerate(components):
        for metal in component:
            metal.signal_index = signal_index

    return new_layout


def signals_to_graph(layout: Layout) -> Graph:
    graph = Graph()

    # The edges are the metals
    for metal in layout.metals:
        graph.add_node(metal)

    metals_by_layer = index_metals_by_layer(layout)

    # Add intersections with vias
    for via in layout.vias:
        # Usually bottom_connections contains the 1 metal connected to the bottom of the via,
        #  and top_connections contains the 1 metal connected to the top of the via, and there is just 1 pair we need to connect.
        # However, sometimes the via may intersect with more metals so we handle that case as well.
        bottom_connections = get_intersecting_metals(via.vertices, metals_by_layer[none_check(via.layer)])
        top_connections = get_intersecting_metals(via.vertices, metals_by_layer[none_check(via.layer) + 1])
        all_connections = bottom_connections + top_connections

        # If there's a connection between two metals, add that connection as an edge.
        for start, end in combinations(all_connections, 2):
            graph.add_edge(start, end)

    # Add intersections metal-to-metal on the same layer
    for layer_metals in metals_by_layer:
        for metal in layer_metals[1]:
            intersecting_metals = get_intersecting_metals(metal.polygon, layer_metals)
            for intersecting in intersecting_metals:
                # No point in connecting a metal to itself
                if intersecting != metal:
                    graph.add_edge(metal, intersecting)


    return graph


def get_intersecting_metals(polygon: list[Point2D], metal_tree: tuple[STRtree, list[Metal]]) -> list[Metal]:
    tree, metals = metal_tree
    shapely_polygon = Polygon(polygon)
    query_result = tree.query(shapely_polygon)
    return [metals[i] for i in query_result if shapely_polygon.intersects(tree.geometries[i])]


def index_metals_by_layer(layout: Layout) -> list[tuple[STRtree, list[Metal]]]:
    """
    Returns a list of metals by layer.
    The layers are indexed in STRtrees for fast access, and the original metals can be retreived from the second item, the list of metals.
    """
    layer_count = max_of(layout.metals, key=lambda m: none_check(m.layer)) + 1
    # Organize polygons by layer
    polygon_list_index: list[list[Metal]] = [[] for _ in range(layer_count)]
    for metal in layout.metals:
        layer = none_check(metal.layer)
        polygon_list_index[layer].append(metal)

    # Optimize layers into STRtrees
    tree_index: list[tuple[STRtree, list[Metal]]] = [
        (STRtree([Polygon(metal.polygon) for metal in metals]), metals) for metals in polygon_list_index
    ]
    return tree_index

# def create_str_trees(layers: list[list[Metal]]) -> list[STRtree]:
    # pass
    # TODO: convert polygon to their polygon
    # return [STRtree(list) for list in layers]


def test_layout_without_signals() -> Layout:
    """
    test layout converted to signal "hard mode", with no signal information.
    """
    new_metals = [Metal(polygon=metal.polygon, layer=metal.layer, signal_index=None, name=metal.name,
                        gds_layer=metal.gds_layer) for metal in test_layout_const.metals]
    return Layout(new_metals, test_layout_const.vias)


if __name__ == "__main__":
    no_signals = test_layout_without_signals()
    traced = trace_signals(no_signals)
    plotly_plot_layout(traced, show_text=True)

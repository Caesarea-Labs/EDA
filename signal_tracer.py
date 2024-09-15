from shapely import STRtree

from Layout import Layout, LayoutPolygon, Metal


def trace_signals(layout: Layout):
    """Will mutate the MetalPolygons in the layout to have the signal_index value set, to match how the metals and vias connect to each other."""
    # by_layer = layout.index_by_layer()
    # for via in layout.vias:
    #     relevant_

    # 1. Get relevant trees for via
    # 2. Check intersection of via with polygons
    pass

# def create_str_trees(layers: list[list[Metal]]) -> list[STRtree]:
    # pass
    # TODO: convert polygon to their polygon
    # return [STRtree(list) for list in layers]
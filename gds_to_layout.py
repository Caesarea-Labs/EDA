from gdstk import Cell, Library, Polygon, Reference, read_gds
from typing import Tuple, cast

import gdstk
import Layout
from cpu_slicing import get_contained_rectangles
from gpu_slicing import GdsPolygonBB, filter_intersecting_rectangles_gpu
from utils import measure_time


def gds_to_layout(gds_file: str, bounding_box: list[tuple[int, int]], metal_layers: list[int], via_layers: list[int]) -> Layout:
    """
    Converts the bounding_box part of a gds file at gds_file to a Caesarea Layout.

    NOTE: in the future we may need to pass data types in addition to the metal/via layers for this to work properly. 
    Currently we assume the data type is always 0.

    :param metal_layers the layers of the gds file containing the metals
    :param via_layers the layers of the gds file containing the vias - the connectors between metals. 
    """

    # We measure the time it takes for the expensive functions

    @measure_time
    def read_gds_timed() -> Library:
        return read_gds(gds_file, filter={(layer, 0) for layer in (metal_layers + via_layers)})

    # Assume data type is 0 always for now
    gds = read_gds_timed()
    cells = cast(list[Cell], gds.top_level())
    assert len(cells) == 1, f"Expected only one top-level cell in gds file {gds_file}."
    cell = cells[0]

    @measure_time
    def get_polygons_timed() -> list[Polygon]:
        return cell.get_polygons(depth=None)

    all_polygons = get_polygons_timed()

    @measure_time
    def prepare_polygon_bounding_boxes() -> list[GdsPolygonBB]:
        return [polygon.bounding_box() for polygon in all_polygons]

    # We do a naive check - only check for the bounding box of the polygons, not their exact vertices. 
    # But this is ok - if the bounding box of the polygon is not inside the desired bounding box, it's ok to discard it. 
    # This makes the slicing much more performant. 
    bounding_boxes = prepare_polygon_bounding_boxes()
    contained_indices = get_contained_rectangles(bounding_boxes,bounding_box)
    contained_polygons = [all_polygons[i] for i in contained_indices]

    print("alo")

    # all_polygons[0].bounding_box()
    # all_polygons_without_repetitions = cell.get_polygons(depth=None, apply_repetitions=False)
    # print("Getting just polygons")
    # just_polygons = cell.polygons
    # x = 2
    # # relevant_layers = metal_layers + via_layers
    # # A bit of a mouthful but it flattens the list of polygons in all relevant layers
    # # relevant_polygons = [polygon for layer in relevant_layers for polygon in cell.get_polygons(depth=None, layer=layer, datatype=0)]

    # # polygons = cell.get_polygons(depth=None)

    # gds_shape = gdstk.Polygon(bounding_box)
    # print("Cutting gds polygons")
    # cut = gdstk.boolean(Reference(cell, (0, 0)), gds_shape, "and")
    # print("Finished cutting gds polygons")
    # x = 2

    # for polygon in cell.polygons:
    #     polygon

# TODO we've implemented rect slicing, we need to add L slicing later as well


if __name__ == "__main__":
    gds_to_layout("test_gds_1.gds",
                    [(1200, 730), (1200, 775), (1390, 775), (1390, 762), (1210, 762), (1210, 730)],
                #   ((1200, 730), (1390, 775)),
                  metal_layers=[61, 62, 63, 64, 65, 66],
                  via_layers=[70, 71, 72, 73, 74]
                  )

import cProfile
from pathlib import Path
from turtle import st
from gdstk import Cell, Library, Polygon, Reference, read_gds
from typing import Tuple, cast

from pyvista import Plotter

from .geometry.geometry import Point2D, Polygon2D, Rect2D, create_polygon
from .layout_inflation import inflate_layout
from .layout import Layout, Metal, Via
from .geometry.polygon_slicing import GdsPolygonBB, cut_polygons, get_contained_rectangles
from .signal_tracer import trace_signals
from .ui.pyvista_gui import plot_layout_with_qt_gui
from .utils import max_of, measure_time, min_of
from .cache import cache_dir

cell_name = "top_io"


def get_gds_top_level_polygons(path: Path) -> list[Polygon]:
    """
    Opens the top-level cell in the gds file in the given path, retreiving all polygons while resolving references.
    """
    library = read_gds(path)
    cells = cast(list[Cell], library.top_level())
    cell = cells[0]
    return cell.get_polygons(depth=None)


def cache_polygons(polygons: list[Polygon], path: Path):
    new_gds = Library()
    new_gds_cell = new_gds.new_cell(cell_name)
    for polygon in polygons:
        new_gds_cell.add(polygon)

    path.parent.mkdir(parents=True, exist_ok=True)
    new_gds.write_gds(path)


def get_filtered_polygons(gds_path: Path, bounding_box: Polygon2D, metal_layers: set[int], via_layers: set[int], cache_key: str) -> list[Polygon]:
    # We cache the filtered polygons in the cache dir
    filtered_gds_cache = cache_dir.joinpath(f"filtered_{cache_key}.gds")
    if filtered_gds_cache.exists():
        return get_gds_top_level_polygons(filtered_gds_cache)

    # We measure the time it takes for the expensive functions

    @measure_time
    def read_gds_timed() -> Library:
        try:
            return read_gds(gds_path, filter={(layer, 0) for layer in (list(metal_layers) + list(via_layers))})
        except:
            raise Exception(f"Could not read GDS file at {gds_path.absolute()}")

    # Assume data type is 0 always for now
    gds = read_gds_timed()
    cells = cast(list[Cell], gds.top_level())
    assert len(cells) == 1, f"Expected only one top-level cell in gds file {gds_path}."
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
    contained_indices = get_contained_rectangles(bounding_boxes, bounding_box, exclusive=False)
    contained_polygons = [all_polygons[i] for i in contained_indices]

    # Cache the filtered gds because this is a long operation
    cache_polygons(contained_polygons, filtered_gds_cache)

    return contained_polygons


def slice_gds_to_layout(gds_file: Path, bounding_box: Polygon2D, metal_layers: set[int], via_layers: set[int], cache_key: str) -> Layout:
    """
    Converts the bounding_box part of a gds file at gds_file to a Caesarea Layout.

    NOTE: in the future we may need to pass data types in addition to the metal/via layers for this to work properly. 
    Currently we assume the data type is always 0.

    :param metal_layers the layers of the gds file containing the metals
    :param via_layers the layers of the gds file containing the vias - the connectors between metals. 
    """

    relevant_polygons = get_filtered_polygons(gds_file, bounding_box, metal_layers, via_layers, cache_key)
    sliced = cut_polygons(relevant_polygons, bounding_box)
    # aligned = align_polygons_to_origin(sliced)

    # cache_polygons(sliced, cache_dir.joinpath("cut.gds"))

    return gds_to_layout(sliced, metal_layers, via_layers)


def align_polygons_to_origin(polygons: list[Polygon]) -> list[Polygon]:
    """
    Translates all polygons by the same x,y, such that there is at least one polygon with x = 0 and y = 0 (and there are no negative values).
    For example, if all polygons are at least x= 500, y = 700, it will translate by (500,700) so that the polygons will be closer to origin.
    """

    min_x = min_of(polygons, key=lambda poly: min_of(poly.points, lambda point: point[0]))
    min_y = min_of(polygons, key=lambda poly: min_of(poly.points, lambda point: point[1]))

    return [polygon.translate(-min_x, -min_y) for polygon in polygons]


def gds_to_layout(polygons: list[Polygon], metal_layers: set[int], via_layers: set[int]) -> Layout:
    metals = [gds_polygon_to_metal(polygon) for polygon in polygons if polygon.layer in metal_layers]
    vias = [gds_polygon_to_via(polygon) for polygon in polygons if polygon.layer in via_layers]
    return Layout(metals=metals, vias=vias)


def gds_polygon_to_metal(polygon: Polygon) -> Metal:
    vertices = [
        Point2D(point[0], point[1]) for point in polygon.points
    ]
    return Metal(
        name="",
        gds_layer=polygon.layer,
        polygon=vertices,
        signal_index=None
    )


def gds_polygon_to_via(polygon: Polygon) -> Via:
    box = polygon.bounding_box()
    return Via(
        name="",
        gds_layer=polygon.layer,
        rect=Rect2D(box[0][0], box[1][0], box[0][1], box[1][1]),
    )


def parse_gds_layout(gds_file: Path, bounding_box: Polygon2D, metal_layers: set[int], via_layers: set[int], cache_key: str) -> Layout:
    layout = slice_gds_to_layout(gds_file,
                                 bounding_box,
                                 metal_layers=metal_layers,
                                 via_layers=via_layers,
                                 cache_key=cache_key
                                 )
    with_layers = inflate_layout(layout)
    return trace_signals(with_layers)


def get_device_gds_layout_test() -> Layout:
    bounds: Polygon2D = create_polygon([(1190, 730), (1190, 790), (1390, 790), (1390, 762), (1210, 762), (1210, 730)])
    return parse_gds_layout(
        Path("gds/test_gds_1.gds"),
        bounds,
        metal_layers={
            10, 30,
            61, 62, 63, 64, 65, 66
        },
        via_layers={
            50,
            70, 71, 72, 73, 74
        },
        cache_key="device_test"
    )


def get_corner_gds_layout_test() -> Layout:
    bounds: Polygon2D = create_polygon([(1200, 730), (1200, 775), (1390, 775), (1390, 762), (1210, 762), (1210, 730)])
    return parse_gds_layout(
        Path("gds/test_gds_1.gds"),
        bounds,
        metal_layers={61, 62, 63, 64, 65, 66},
        via_layers={70, 71, 72, 73, 74},
        cache_key="corner_test"
    )


# def get_oleg_gds_layout() -> Layout:
#     bounds = create_polygon([(21, 47), (40, 47), (40, 42), (21, 42)])
#     return parse_gds_layout(
#         Path("gds/oleg_gds.gds"),
#         bounds,
#         metal_layers={}
#     )


@measure_time
def main():
    # layout = slice_gds_to_layout(Path("test_gds_1.gds"),
    #                              create_polygon([(1200, 730), (1200, 775), (1390, 775), (1390, 762), (1210, 762), (1210, 730)]),
    #                              metal_layers={61, 62, 63, 64, 65, 66},
    #                              via_layers={70, 71, 72, 73, 74}
    #                              )
    # with_layers = inflate_layout(layout)
    # with_signal = trace_signals(with_layers)

    cProfile.run("plot_layout_with_qt_gui(get_large_gds_layout_test())")

    # plotter = Plotter()
    # plot_layout(get_large_gds_layout_test(), show_text=False, plotter=plotter)

    # plotly_plot_layout(with_signal, show_text=False)


if __name__ == "__main__":
    main()

# Next step: turning off layers selectively using github example with s

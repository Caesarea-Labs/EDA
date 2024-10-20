from eda.Shapes import rect_shape
from eda.geometry.geometry import Rect2D
from eda.layout import Layout, Metal, Via
from eda.layout_inflation import build_gds_layer_mapping, inflate_layout
from eda.ui.pyvista_gui import plot_layout_with_qt_gui
from eda.utils import none_check
from .test_layout import test_layout_const


def test_simple_inflation():
    mapping = build_gds_layer_mapping(
        metal_gds_layer_order=[10,11,12,13,14],
        via_gds_layers=[20,21,22,23]
    )
    inflated = inflate_layout(scramble_layout(test_layout_const), mapping)
    plot_layout_with_qt_gui(inflated, show_polygon_names=True)
    # plot_layout_with_qt_gui(test_layout_const, show_polygon_names=True)


def test_hybrid_via_layer_inflation():
    # TODO: test when there are more normal layers above it

    # 3. Allow merging layers when inflating layouts
    # 4. When signal tracing, ignore diffusion layers since they are connected to everything
    # plot_layout_with_qt_gui(expected_layout)

    scrambled_layout = Layout(
        metals=[
            rect_shape(width=5, height=5, name="base").metal(gds_layer=20),
            rect_shape(width=1, height=3, name="m1").translate(0.5, 0.5).metal(gds_layer=21, signal_index=1),
            rect_shape(width=1, height=3, name="m2").translate(2.5, 0.5).metal(gds_layer=21, signal_index=1),
            rect_shape(width=3, height=1, name="t1").translate(0.5, 0.5).metal(gds_layer=22, signal_index=2),
            rect_shape(width=8, height=1, name="t2").translate(0.5, 2.5).metal(gds_layer=22, signal_index=2),
            rect_shape(width=3, height=1, name="t3").translate(0.5, 2.5).metal(gds_layer=23, signal_index=3),
            rect_shape(width=5, height=5, name="t3").translate(6.5, 2.5).metal(gds_layer=24, signal_index=0),
        ],
        vias=[
            Via(
                gds_layer=11,
                rect=Rect2D(x_start=2, x_end=2.2, y_start=0.9, y_end=1.1),
                name="a"
            ),
            Via(
                gds_layer=11,
                rect=Rect2D(x_start=1.1, x_end=1.3, y_start=2.9, y_end=3.1),
                name="b"
            ),
            Via(
                gds_layer=12,
                rect=Rect2D(x_start=1.0, x_end=1.2, y_start=2.9, y_end=3.1),
                name="c"
            ),
            Via(
                gds_layer=11,
                rect=Rect2D(x_start=7.0, x_end=7.2, y_start=2.9, y_end=3.1),
                name="c"
            )
        ]
    )

    mapping = build_gds_layer_mapping(
        metal_gds_layer_order=[[20, 24], 21, 22, 23],
        via_gds_layers=[[11], 12]
    )

    inflated = inflate_layout(scrambled_layout, mapping)
    plot_layout_with_qt_gui(inflated, show_polygon_names=True)

# AssertionError: More than two possible metal layers could be connected to via layer 21: [10, 11, 12].
#  All of the vias on that level hit metals in all layers equally (1 times).


def scramble_layout(layout: Layout) -> Layout:
    """
    test layout converted to "hard mode", with no proper information on layers, but with less-reliable gds_layer information.
    """
    new_metals = [Metal(polygon=metal.polygon, layer=None, signal_index=metal.signal_index, name=metal.name,
                        gds_layer=none_check(metal.layer) + 10) for metal in layout.metals]
    new_vias = [Via(
                gds_layer=none_check(via.bottom_layer) + 20,
                bottom_layer=None,
                rect=via.rect,
                name=via.name
                ) for via in layout.vias]
    return Layout(new_metals, new_vias)

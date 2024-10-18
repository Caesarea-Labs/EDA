from eda.Shapes import rect_shape
from eda.geometry.geometry import Rect2D
from eda.layout import Layout, Metal, Via
from eda.layout_inflation import inflate_layout
from eda.ui.pyvista_gui import plot_layout_with_qt_gui
from eda.utils import none_check
from tests import test_layout
from test_layout import test_layout_const

def test_simple_inflation():
    inflated = inflate_layout(scramble_layout(test_layout_const))
    # plotly_plot_layout(inflated, show_text=True)


def test_hybrid_via_layer_inflation():
    # TODO: test when there are more normal layers above it
    expected_layout = Layout(
        metals=[
            rect_shape(width=3, height=5, name="base").translate(2,0).metal(layer = 0),
            rect_shape(width=1, height=3, name="m1").translate(0.5,0.5).metal(layer = 1, signal_index=1),
            rect_shape(width=1, height=3, name="m2").translate(2.5, 0.5).metal(layer = 1, signal_index=1),
            rect_shape(width=3, height=1, name="t1").translate(0.5, 0.5).metal(layer = 2, signal_index=2),
            rect_shape(width=3, height=1, name="t2").translate(0.5, 2.5).metal(layer = 2, signal_index=2),
        ],
        vias=[
            Via(
                top_layer=2,
                bottom_layer=0,
                rect=Rect2D(x_start=2, x_end=2.2, y_start=0.9, y_end=1.1),
                name="a"
            ),
            Via(
                top_layer=2,
                bottom_layer=1,
                rect=Rect2D(x_start=1.1, x_end=1.3, y_start=2.9, y_end=3.1),
                name="b"
            ),
        ]
    )

    # 2. Adjust algorithm to figure out cases where the bottom_layer isn't top_layer-1
    # 3. Allow merging layers when inflating layouts
    # 4. When signal tracing, ignore diffusion layers since they are connected to everything
    # 5. Allow passing some sort of forced order to force the diffusion layers to be at the bottom 
    # (this would replace the min() call in find_lowest_layer and the sorted() call in get_via_layer_connected_metal_layers)

    # plot_layout_with_qt_gui(expected_layout)

    scrambled_layout = Layout(
        metals=[
            rect_shape(width=3, height=5, name="base").translate(2,0).metal(gds_layer= 20),
            rect_shape(width=1, height=3, name="m1").translate(0.5,0.5).metal(gds_layer= 21, signal_index=1),
            rect_shape(width=1, height=3, name="m2").translate(2.5, 0.5).metal(gds_layer= 21, signal_index=1),
            rect_shape(width=3, height=1, name="t1").translate(0.5, 0.5).metal(gds_layer= 22, signal_index=2),
            rect_shape(width=3, height=1, name="t2").translate(0.5, 2.5).metal(gds_layer= 22, signal_index=2),
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
        ]
    )

    inflated = inflate_layout(scrambled_layout)


#AssertionError: More than two possible metal layers could be connected to via layer 21: [10, 11, 12].       
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
from Draw import plot_layout
from Layout import Layout, Via, Rect2D
from Shapes import L_shape, lamed_shape, rect_shape

shape = lamed_shape(1, 3, 2, 2)
test_layout = Layout(metals=[
    shape.named("A").metal(0, 0),
    shape.named("B").translate(6, 5).metal(0, 0),

    shape.named("C").translate(1, 1).metal(1, 0),
    shape.named("D").translate(8, 6).metal(1, 1),

    shape.named("E").translate(0, 6).metal(2, 2),
    lamed_shape(1, 5, 2, 2, name="F").rotate(270).mirror_vertical().translate(8, 2).metal(2, 2),

    lamed_shape(1, 4, 2, 2, name="G").translate(0, 3).metal(3, 2),
    shape.named("H").translate(8, 7).metal(3, 1),

    shape.named("I").translate(4, 4).metal(4, 0),

    rect_shape(width=2, height=1, name="d_int").translate(10, 10).metal(2, 1),

    rect_shape(width=1, height=1, name="b_int1").translate(6, 8).metal(1, 0),
    rect_shape(width=1, height=1, name="b_int2").translate(6, 8).metal(2, 0),
    rect_shape(width=1, height=1, name="b_int3").translate(6, 8).metal(3, 0),

    rect_shape(width=1, height=1, name="c_int1").translate(4, 5).metal(2, 0),
    rect_shape(width=1, height=1, name="c_int2").translate(4, 5).metal(3, 0),

],
    vias=[
        Via(
            layer=0,
            rect=Rect2D(x_start=3, x_end=5, y_start=4, y_end=6),
            name="a"
        ),
        Via(
            layer=0,
            rect=Rect2D(x_start=6, x_end=7, y_start=8, y_end=9),
            name="b1"
        ),
        Via(
            layer=1,
            rect=Rect2D(x_start=6, x_end=7, y_start=8, y_end=9),
            name="b2"
        ),
        Via(
            layer=2,
            rect=Rect2D(x_start=6, x_end=7, y_start=8, y_end=9),
            name="b3"
        ),
        Via(
            layer=3,
            rect=Rect2D(x_start=6, x_end=7, y_start=8, y_end=9),
            name="b4"
        ),
        Via(
            layer=1,
            rect=Rect2D(x_start=4, x_end=5, y_start=5, y_end=6),
            name="c1"
        ),
        Via(
            layer=2,
            rect=Rect2D(x_start=4, x_end=5, y_start=5, y_end=6),
            name="c2"
        ),
        Via(
            layer=3,
            rect=Rect2D(x_start=4, x_end=5, y_start=5, y_end=6),
            name="c3"
        ),
        Via(
            layer=1,
            rect=Rect2D(x_start=10, x_end=12, y_start=10, y_end=11),
            name="d1"
        ),
        Via(
            layer=2,
            rect=Rect2D(x_start=10, x_end=12, y_start=10, y_end=11),
            name="d2"
        ),
        Via(
            layer=2,
            rect=Rect2D(x_start=1, x_end=2, y_start=6, y_end=8),
            name="e"
        ),
        Via(
            layer=2,
            rect=Rect2D(x_start=1, x_end=2, y_start=3, y_end=4),
            name="f"
        )
    ]
)

# TODO:
# 1. Allow not specifying signals, and have it resolve the signals itself
# 2. Have it attempt to connect 2 signals ('via edit')
# 3. convert large GDS to our format for large input testing

plot_layout(test_layout, 14, 5)

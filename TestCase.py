from Draw import plot_layout
from Layout import MetalPolygon, Via, Point2D, Rect2D, Layout
from Shapes import s_shape, lamed_shape, L_shape, rectangle_shape

connection = Via(
    bottomLayer=1,
    topLayer=3,
    rect=Rect2D(x_start=2, x_end=3, y_start=3, y_end=4)
)

layout = Layout([
    s_shape.layer(0),
    L_shape.layer(1),
    lamed_shape.layer(2),
    rectangle_shape.layer(3),
] , [])
plot_layout(layout)

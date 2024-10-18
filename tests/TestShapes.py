from eda.layout import Via,Rect2D, Layout
from eda.Shapes import s_shape, lamed_shape, L_shape, rect_shape

# connection = Via(
#     layer=1,
#     rect=Rect2D(x_start=2, x_end=3, y_start=3, y_end=4)
# )

# test_lamed_shape = lamed_shape(2, 2, 2, 2)
# test_s_Shape = s_shape(2, 2, 2, 2)
# test_l_shape = L_shape(2, 1, 1, 1)
# test_rect_shape = rect_shape(1, 1)
# layout = Layout([
#     # s_shape(2,3,2, 2).layer(0),
#     # s_shape(1,1,2, 2).translate(4,4).layer(1),
#     # test_lamed_shape.translate(0, 0).layer(2),
#     # test_lamed_shape.translate(4, 4).rotate(90).layer(3),
#     # test_lamed_shape.translate(8, 8).mirror_horizontal().layer(4),
#     # test_lamed_shape.translate(12, 12).mirror_vertical().layer(5),

#     # test_l_shape.translate(0, 0).layer(2),
#     # test_l_shape.translate(4, 4).rotate(90).layer(3),
#     # test_l_shape.translate(12, 4).rotate(180).layer(3),
#     # test_l_shape.translate(4, 12).rotate(270).layer(3),
#     # test_l_shape.translate(8, 8).mirror_horizontal().layer(4),
#     # test_l_shape.translate(12, 12).mirror_vertical().layer(5),

#     # test_s_Shape.translate(0, 0).layer(2),
#     # test_s_Shape.translate(4, 4).rotate(90).layer(3),
#     # test_s_Shape.translate(12, 4).rotate(180).layer(3),
#     # test_s_Shape.translate(4, 12).rotate(270).layer(3),
#     # test_s_Shape.translate(8, 8).mirror_horizontal().layer(4),
#     # test_s_Shape.translate(12, 12).mirror_vertical().layer(5),

#     rect_shape(1, 1).metal(1),
#     rect_shape(1, 2).translate(5, 5).metal(2),
#     rect_shape(2, 1).translate(10, 10).metal(3),
#     rect_shape(3, 3).translate(0, 10).metal(4),

#     # test_s_Shape.translate(0, 0).layer(2),
#     # test_s_Shape.translate(4, 4).rotate(90).layer(3),
#     # test_s_Shape.translate(8, 8).rotate(180).layer(4),
#     # test_s_Shape.translate(12, 12).rotate(270).layer(5),
#     # L_shape.layer(1),
#     # lamed_shape.layer(2),
#     # rectangle_shape.layer(3),
# ], [

# ])
# plotly_plot_layout(layout, show_text=False)

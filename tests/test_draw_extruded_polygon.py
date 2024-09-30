from pyvista import Plotter
from eda import test_layout
from eda.ui.layout_plot import plot_meshes
from eda.geometry.geometry import Point2D
from eda.polygon_triangulizer import ExtrudedPolygon, polygon_to_mesh
from eda.ui.pyvista_gui_test import plot_layout_with_qt_gui


def test_draw_extruded_polygon():
    polygon_1 = ExtrudedPolygon(
        z_base=0, z_top=1,
        vertices=[
            Point2D(0, 0),  # Bottom-left corner
            Point2D(2, 0),  # Bottom-right corner
            Point2D(2, 1),  # Middle-right corner
            Point2D(3, 1),  # Middle-right overhang
            Point2D(3, 2),  # Top-right overhang
            Point2D(1, 2),  # Top-left corner of overhang
            Point2D(1, 1),  # Middle-left corner
            Point2D(0, 1)   # Back to bottom-left corner
        ],
        color="blue", alpha=0.3, name="test1", group_name="2"
    )

    polygon_2 = ExtrudedPolygon(
        z_base=10, z_top=11,
        vertices=[
            Point2D(0, 0),  # Bottom-left corner
            Point2D(2, 0),  # Bottom-right corner
            Point2D(2, 1),  # Middle-right corner
            Point2D(3, 1),  # Middle-right overhang
            Point2D(3, 2),  # Top-right overhang
            Point2D(1, 2),  # Top-left corner of overhang
            Point2D(1, 1),  # Middle-left corner
            Point2D(0, 1)   # Back to bottom-left corner
        ],
        color="blue", alpha=0.3, name="test2", group_name="2"
    )

    plot_meshes([
        polygon_to_mesh(polygon_1), polygon_to_mesh(polygon_2)
    ], show_text=True,plotter= Plotter())

    

def test_draw_test_layout():
    plot_layout_with_qt_gui(test_layout.test_layout_const)
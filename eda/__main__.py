import cProfile
from eda import test_layout
from .gds_to_layout import get_large_gds_layout_test
from .ui.pyvista_gui_test import plot_layout_with_qt_gui


if __name__ == "__main__":
    plot_layout_with_qt_gui(get_large_gds_layout_test())
    # plot_layout_with_qt_gui(test_layout.test_layout_const)
    # cProfile.run('plot_layout_with_qt_gui(get_large_gds_layout_test())', filename="eda.prof")
    
import cProfile
import os
# os.environ["QT_API"] = "pyqt6"

from pyvista import Plotter
from eda import test_layout
from eda.ui.layout_plot import plot_layout
from .gds_to_layout import get_large_gds_layout_test
from .ui.pyvista_gui_test import plot_layout_with_qt_gui

# def main():
#     # plot_layout_with_qt_gui(get_large_gds_layout_test())
#     # plot_layout_with_qt_gui(test_layout.test_layout_const)
#     plot_layout(test_layout.test_layout_const, show_text=False, plotter=Plotter())



if __name__ == "__main__":
    # plot_layout(get_large_gds_layout_test(), show_text=False, plotter=Plotter())
    plot_layout_with_qt_gui(get_large_gds_layout_test())
    # plot_layout_with_qt_gui(test_layout.test_layout_const)
    # plot_layout(test_layout.test_layout_const, show_text=False, plotter=Plotter())

    # plot_layout_with_qt_gui(test_layout.test_layout_const)
    # plot_layout_with_qt_gui(test_layout.test_layout_const)
    # cProfile.run('plot_layout_with_qt_gui(get_large_gds_layout_test())', filename="eda.prof")
    
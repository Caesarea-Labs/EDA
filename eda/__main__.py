#
import os

os.environ["QT_API"] = "pyside6"

from .gds_to_layout import get_large_gds_layout_test
from .ui.pyvista_gui import plot_layout_with_qt_gui


def main():
    plot_layout_with_qt_gui(get_large_gds_layout_test())
    # plot_layout_with_qt_gui(get_large_gds_layout_test())
    # plot_layout_with_qt_gui(test_layout.test_layout_const)
    # plot_layout(test_layout.test_layout_const, show_text=False, plotter=Plotter())


if __name__ == "__main__":
    # plot_layout(get_large_gds_layout_test(), show_text=False, plotter=Plotter())
    plot_layout_with_qt_gui(get_large_gds_layout_test())
    # plot_layout(test_layout.test_layout_const, show_text=False, plotter=Plotter())

    # plot_layout_with_qt_gui(test_layout.test_layout_const)
    # plot_layout_with_qt_gui(test_layout.test_layout_const)
    # cProfile.run('plot_layout_with_qt_gui(get_large_gds_layout_test())', filename="eda.prof")

#
import cProfile
import os

from eda.genetic_via_placement import get_test_ga_circuit_edit

os.environ["QT_API"] = "pyside6"

from .gds_to_layout import get_corner_gds_layout_test, get_device_gds_layout_test
from .ui.pyvista_gui import plot_layout_with_qt_gui


def main():
    # cProfile.runctx('get_test_ga_circuit_edit(plot = False, cache = False)', globals(), locals(), filename="eda.prof")
    # plot_layout_with_qt_gui(get_test_ga_circuit_edit())
    # plot_layout_with_qt_gui(get_device_gds_layout_test())
    # plot_layout_with_qt_gui(get_corner_gds_layout_test())
    plot_layout_with_qt_gui(get_test_ga_circuit_edit(plot = False, cache = False))
    # plot_layout_with_qt_gui(get_large_gds_layout_test())
    # plot_layout_with_qt_gui(test_layout.test_layout_const)
    # plot_layout(test_layout.test_layout_const, show_text=False, plotter=Plotter())


if __name__ == "__main__":
    main()
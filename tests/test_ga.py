from eda.genetic_via_placement import get_test_ga_circuit_edit
from eda.ui.pyvista_gui import plot_layout_with_qt_gui


def test_draw_ga_CE():
    layout = get_test_ga_circuit_edit()
    plot_layout_with_qt_gui(layout)
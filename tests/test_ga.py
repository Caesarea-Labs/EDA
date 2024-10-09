from eda.genetic_via_placement import get_test_ga_circuit_edit
from eda.ui.layout_plot import plot_layout_standalone
from eda.ui.pyvista_gui import plot_layout_with_qt_gui


# def test_draw_ga_CE():
#     layout = get_test_ga_circuit_edit()
#     plot_layout_with_qt_gui(layout)

def test_draw_ga_CE_no_gui():
    layout = get_test_ga_circuit_edit()
    plot_layout_standalone(layout)
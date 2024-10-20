from eda.circuitedit.circuit_edit_cut import get_test_ga_circuit_edit_cut
from eda.circuitedit.circuit_edit_via import get_test_ga_circuit_edit
from eda.ui.layout_plot import plot_layout_standalone
from eda.ui.pyvista_gui import plot_layout_with_qt_gui


# def test_draw_ga_CE():
#     layout = get_test_ga_circuit_edit()
#     plot_layout_with_qt_gui(layout)

def test_draw_ga_CE():
    layout = get_test_ga_circuit_edit()
    plot_layout_with_qt_gui(layout)

def test_draw_ga_CE_small_signals():
    layout = get_test_ga_circuit_edit(cache = False, signal_a=2, signal_b=5, plot=False)
    plot_layout_with_qt_gui(layout)

def test_CE_cut():
    layout = get_test_ga_circuit_edit_cut(cache = False)

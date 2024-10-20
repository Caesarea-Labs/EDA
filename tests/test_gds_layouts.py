from eda.gds_to_layout import get_device_gds_layout_test
from eda.ui.pyvista_gui import plot_layout_with_qt_gui


def test_device_gds_layout():
    print("Alo")
    plot_layout_with_qt_gui(get_device_gds_layout_test())

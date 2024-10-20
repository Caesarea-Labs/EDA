from eda.layout import Layout, Metal
from eda.signal_tracer import trace_signals
from .test_layout import test_layout_const

def test_layout_without_signals() -> Layout:
    """
    test layout converted to signal "hard mode", with no signal information.
    """
    new_metals = [Metal(polygon=metal.polygon, layer=metal.layer, signal_index=None, name=metal.name,
                        gds_layer=metal.gds_layer) for metal in test_layout_const.metals]
    return Layout(new_metals, test_layout_const.vias)


def test_signal_tracing():
    no_signals = test_layout_without_signals()
    traced = trace_signals(no_signals)
    # plotly_plot_layout(traced, show_text=True)

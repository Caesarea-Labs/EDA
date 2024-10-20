from shapely import Polygon
from eda.geometry.geometry_utils import PolygonIndex
from eda.geometry.geometry import Polygon2D
from eda.layout import Layout, Metal
from eda.utils import none_check

def metal_polygon(metal: Metal) -> Polygon2D:
    return metal.polygon
def index_layout_metals(layout: Layout)-> PolygonIndex[Metal]:
    return PolygonIndex([metal for metal in layout.metals], metal_polygon)

def index_layout_signal_by_layer(layout: Layout, signal: int) -> list[PolygonIndex[Metal]]:
    metals_by_layer = layout.metals_by_layer()
    signal_metals_by_layer = [
        PolygonIndex([metal for metal in layer_metals if metal.signal_index == signal], metal_polygon) for layer_metals in metals_by_layer
    ]
    return signal_metals_by_layer

def get_metal_count_above_polygon(polygon: Polygon, above_layer: int, metals: PolygonIndex[Metal]) -> int:
    # Only metals above this via pose a problem
    return len([metal for metal in metals.get_intersecting(polygon) if none_check(metal.layer) > above_layer])
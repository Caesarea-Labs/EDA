import numpy as np
from eda.layout import Layout, Metal
from eda.utils import max_of, min_of, none_check
from eda.geometry.geometry import Polygon2D, Rect3D
from numpy.typing import NDArray


def calculate_signal_bounds(layout: Layout, signal: int) -> Rect3D:
    """
    Calculates the area in whcih the GA should generate numbers
    """

    polygons = [
        point for metal in layout.metals if metal.signal_index == signal
        for point in metal.polygon
    ]
    metals = [metal for metal in layout.metals if metal.signal_index == signal]

    # The bounds for all 6 dimensions of the GA
    return Rect3D.from_bounds(
        x_min=min_of(polygons, lambda p: p.x),
        y_min=min_of(polygons, lambda p: p.y),
        x_max=max_of(polygons, lambda p: p.x),
        y_max=max_of(polygons, lambda p: p.y),
        z_min=min_of(metals, lambda m: none_check(m.layer)),
        z_max=max_of(metals, lambda m: none_check(m.layer))
    )

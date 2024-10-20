from math import floor
from typing import Sequence
from matplotlib import axes
from matplotlib.pyplot import show, subplots, tight_layout
from numpy import ndarray
from eda.geometry.fast_area_intersection import intersecting_area, intersection
from eda.geometry.geometry import Point2D, Rect2D, Polygon2D
from matplotlib.patches import Polygon

from eda.utils import max_of, min_of


# def test_area_intersect():
#     rect = Rect2D(x_start=0, x_end=10, y_start=0, y_end=10)
#     # Define some overlapping polygons
#     polygons = [
#         [Point2D(2, 2), Point2D(8, 2), Point2D(8, 8), Point2D(2, 8)],  # Square inside the rectangle
#         [Point2D(5, 5), Point2D(12, 5), Point2D(12, 12), Point2D(5, 12)],  # Overlaps with the first polygon
#         [Point2D(0, 0), Point2D(15, 0), Point2D(15, 15), Point2D(0, 15)]   # Encompasses the rectangle
#     ]

#     # Calculate the total intersected area
#     intersected_area = intersecting_area(rect, polygons)
#     print(f"Total intersected area: {intersected_area}")


def test_intersection():
    rect = Rect2D(x_start=0, x_end=10, y_start=0, y_end=10).as_polygon()
    # Define some overlapping polygons
    polygon_a: Polygon2D = [Point2D(2, 2), Point2D(8, 2), Point2D(8, 8), Point2D(2, 8)]  # Square inside the rectangle
    polygon_b: Polygon2D = [Point2D(5, 5), Point2D(12, 5), Point2D(12, 12), Point2D(5, 12)]  # Overlaps with the first polygon
    polygon_c: Polygon2D = [Point2D(0, 0), Point2D(15, 0), Point2D(15, 15), Point2D(0, 15)]   # Encompasses the rectangle

    plot_polygons({
        "Polygons 1": [rect, polygon_a], "Intersection 1": [intersection(rect, polygon_a)],
        "Polygons 2": [rect, polygon_b], "Intersection 2": [intersection(rect, polygon_b)],
        "Polygons 3": [rect, polygon_c], "Intersection 3": [intersection(rect, polygon_c)]
    })


colors = ["red", "green", "blue", "cyan", "magenta", "yellow"]


def plot_polygons(polygon_groups: dict[str, list[Polygon2D]]):
    x_min = min_of(polygon_groups.values(), lambda polygons: min_of(polygons, key=lambda poly: min_of(poly, key=lambda p: p.x))) 
    x_max = max_of(polygon_groups.values(), lambda polygons: max_of(polygons, key=lambda poly: max_of(poly, key=lambda p: p.x))) 
    y_min = min_of(polygon_groups.values(), lambda polygons: min_of(polygons, key=lambda poly: min_of(poly, key=lambda p: p.y))) 
    y_max = max_of(polygon_groups.values(), lambda polygons: max_of(polygons, key=lambda poly: max_of(poly, key=lambda p: p.y))) 
    groups = len(polygon_groups)
    fig, axis = subplots(floor(groups / 2), 2)
    for i, (group_name, polygons) in enumerate(polygon_groups.items()):
        ax: axes.Axes = axis[floor(i / 2), i %2] if isinstance(axis, ndarray) else axis[i] 
        for i, polygon in enumerate(polygons):
            mpl_polygon = Polygon(
                xy=[[p.x, p.y] for p in polygon],
                closed=True, fill=True, edgecolor=colors[i], facecolor=colors[i], alpha=0.5
            )
            ax.add_patch(mpl_polygon)


        # # Set the limits of the plot
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)

        # Set aspect ratio to be equal
        ax.set_aspect('equal')

        # Add grid, labels, and title (optional)
        ax.grid(True)
        ax.set_xlabel('X-axis')
        ax.set_ylabel('Y-axis')
        ax.set_title(group_name)

    # Show the plot
    tight_layout()
    show()

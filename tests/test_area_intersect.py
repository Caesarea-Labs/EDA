from eda.geometry.fast_area_intersection import intersecting_area
from eda.geometry.geometry import Point2D, Rect2D


def test_area_intersect():
    rect = Rect2D(x_start=0, x_end=10, y_start=0, y_end=10)
    # Define some overlapping polygons
    polygons = [
        [Point2D(2, 2), Point2D(8, 2), Point2D(8, 8), Point2D(2, 8)],  # Square inside the rectangle
        [Point2D(5, 5), Point2D(12, 5), Point2D(12, 12), Point2D(5, 12)],  # Overlaps with the first polygon
        [Point2D(0, 0), Point2D(15, 0), Point2D(15, 15), Point2D(0, 15)]   # Encompasses the rectangle
    ]

    # Calculate the total intersected area
    intersected_area = intersecting_area(rect, polygons)
    print(f"Total intersected area: {intersected_area}")
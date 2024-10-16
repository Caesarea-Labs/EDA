from shapely import box

from eda.geometry.fast_area_intersection import remove_polygon_overlaps


def test_remove_polygon_overlaps():
    polygons = [
        box(0, 1, 3, 2),
        box(1, 0, 2, 3)
    ]

    print(remove_polygon_overlaps(polygons))
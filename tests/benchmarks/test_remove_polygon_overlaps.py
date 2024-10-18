from shapely import Polygon, box

from eda.geometry.fast_area_intersection import remove_polygon_overlaps
from eda.utils import find


def test_remove_overlaps_plus():
    # Plus shape
    polygons = [
        box(0, 1, 3, 2),
        box(1, 0, 2, 3)
    ]
    assert_polygon_result_equals(polygons, {
        Polygon([(3, 1), (3, 2), (0, 2), (0, 1)]),
        Polygon([(2, 0), (1, 0), (1, 1), (2, 1)]),
        Polygon([(1, 3), (2, 3), (2, 2), (1, 2)]),
    })


def test_remove_overlaps_slight():
    polygons = [
        box(0, 0, 2, 2),
        box(1, 0, 3, 2)
    ]

    assert_polygon_result_equals(polygons, {
        box(0, 0, 2, 2),
        box(2, 0, 3, 2)
    })


def test_remove_overlaps_double_overlap():
    polygons = [
        box(0, 0, 3, 2),
        box(1, 0, 4, 2),
        box(2, 0, 5, 2),
    ]

    assert_polygon_result_equals(polygons, {
        box(0, 0, 3, 2),
        box(3, 0, 4, 2),
        box(4, 0, 5, 2)
    })


def test_remove_overlaps_complex_overlaps():
    polygons = [
        box(1, 1, 5, 6),
        box(2, 2, 7, 5),
        Polygon([
            (4, 7),
            (6, 7),
            (6, 4),
            (4, 3)
        ])
    ]

    # print(remove_polygon_overlaps(polygons))
    assert_polygon_result_equals(polygons, {
        box(1, 1, 5, 6),
        box(5, 2, 7, 5),
        Polygon([
            (6, 5),
            (5, 5),
            (5, 6),
            (4, 6),
            (4, 7),
            (6, 7)
        ])
    })


def test_remove_overlaps_chatgpt_cases():
    # Test Set 1 (Simple Squares Overlapping)
    assert_polygons_wont_overlap_with_algorithm([
        box(0, 0, 3, 3),
        box(2, 2, 5, 5),
        box(1, 1, 4, 4)
    ])
    # Test Set 2 (L-shapes Overlapping)
    assert_polygons_wont_overlap_with_algorithm(
        [
            Polygon([(0, 0), (0, 3), (1, 3), (1, 1), (3, 1), (3, 0), (0, 0)]),
            Polygon([(2, 2), (2, 5), (3, 5), (3, 3), (5, 3), (5, 2), (2, 2)])
        ]
    )
    # Test Set 3 (Triangles and Quadrilaterals Overlapping)
    assert_polygons_wont_overlap_with_algorithm(
        [
            Polygon([(0, 0), (3, 0), (1.5, 2)]),
            Polygon([(2, 1), (4, 1), (3, 3), (1, 3)]),
            Polygon([(2, 0), (3, 0), (2.5, 1)])
        ]
    )
    # Test Set 4 (Nested Polygons)
    assert_polygons_wont_overlap_with_algorithm(
        [
            box(0, 0, 10, 10),
            box(2, 2, 8, 8),
            box(4, 4, 6, 6)
        ]
    )
    # Test Set 5 (Complex Overlapping Polygons)
    assert_polygons_wont_overlap_with_algorithm(
        [
            Polygon([(0, 0), (2, 4), (4, 0), (0, 0)]),
            Polygon([(1, 1), (3, 5), (5, 1), (1, 1)]),
            Polygon([(2, 0), (4, 0), (4, 4), (2, 4), (2, 0)])
        ]
    )

    # Test Set 6: Many Polygons Spread Around
    assert_polygons_wont_overlap_with_algorithm(
        [
            # Spread-out polygons
            box(0, 0, 3, 3),          # Square in bottom-left corner
            box(10, 10, 13, 13),      # Square far from the first one
            box(5, 15, 9, 19),        # Rectangle at the top-right
            Polygon([(15, 0), (17, 3), (16, 6), (14, 3)]),  # Diamond shape far right
            Polygon([(3, 10), (6, 10), (6, 12), (3, 12)]),  # Rectangle at middle-left
            # Overlapping polygons
            box(5, 5, 9, 9),          # Square near center
            box(7, 7, 11, 11),        # Overlapping square in center
            Polygon([(8, 2), (12, 2), (10, 4)]),  # Triangle at the bottom-right
            # Isolated polygon
            Polygon([(20, 20), (23, 23), (21, 25), (19, 22)])  # Random quadrilateral far away
        ]
    )


def assert_polygon_result_equals(input: list[Polygon], expected_output: set[Polygon]):
    """
    Checks that running remove_polygon_overlaps on the input list results in the same polygons specified as the expected output.
    """
    assert_polygons_wont_overlap_with_algorithm(input)

    without_overlaps = remove_polygon_overlaps(input)
    for output in without_overlaps:
        equal_expected = find(expected_output, key=lambda poly: poly.equals(output))
        if equal_expected is None:
            raise AssertionError(f"Result polygon {output} is not one of the expected polygons: {expected_output}")
        else:
            # Avoid having one item in the without_overlaps being equal to multiple items in the expected output
            expected_output.remove(equal_expected)


def assert_polygons_wont_overlap_with_algorithm(input: list[Polygon]):
    """
    Checks that remove_polygon_overlaps results in non-overlapping polygons
    """
    without_overlaps = remove_polygon_overlaps(input)
    for output in without_overlaps:
        for other_output in without_overlaps:
            if other_output != output:
                assert output.intersection(other_output).area == 0

from .geometry.polygon_slicing import GdsPolygonBB, get_contained_rectangles
# from gpu_slicing import GdsPolygonBB, filter_intersecting_rectangles_gpu


# Various methods for creating test rectangles to test intersections on
def square(xy: tuple[float, float], size: int) -> GdsPolygonBB:
    x, y = xy
    return ((x, y), (x + size, y + size))


def rectWide(xy: tuple[float, float], width: int) -> GdsPolygonBB:
    x, y = xy
    return ((x, y), (x + width, y + 20))


def rectTall(xy: tuple[float, float], height: int) -> GdsPolygonBB:
    x, y = xy
    return ((x, y), (x + 20, y + height))


# Example Usage
if __name__ == "__main__":
    intersecting_points = [
        (x * 10 + 0.1, y * 10 + 0.1) for y in range(5) for x in range(5)
    ]

    another_non_intersecting = [square((200, 200), 20)]

    intersecting_rectangles = [rectangle for point in intersecting_points for (rectangle) in [
        square(point, 20), square(point, 40), square(point, 60),
        rectWide(point, 40), rectWide(point, 60),
        rectTall(point, 20), rectTall(point, 40)
    ]]

    # non_intersecting_points = []
    non_intersecting_rectangles = [
        ((0, 0), (5, 5)),
        ((0, 0), (200, 5)),
        ((0, 0), (5, 200)),
        ((70, 0), (200, 200)),
        ((0, 70), (200, 200)),
        ((70, 70), (200, 200)),
    ]

    all_rectangles = another_non_intersecting + intersecting_rectangles + non_intersecting_rectangles
    bounding_box = [(10, 10), (10, 50), (50, 50), (50, 10)]

    filtered_indices_cpu = get_contained_rectangles(all_rectangles, bounding_box)
    filtered_cpu = [all_rectangles[i] for i in filtered_indices_cpu]

    expected_result = [
        ((10.1, 10.1), (30.1, 30.1)),
        ((10.1, 10.1), (30.1, 30.1)),
        ((20.1, 10.1), (40.1, 30.1)),
        ((20.1, 10.1), (40.1, 30.1)),
        ((10.1, 20.1), (30.1, 40.1)),
        ((10.1, 20.1), (30.1, 40.1)),
        ((20.1, 20.1), (40.1, 40.1)),
        ((20.1, 20.1), (40.1, 40.1))
    ]

    for i in range(max(len(expected_result), len(filtered_cpu))):
        orig = expected_result[i]
        filtered_element = filtered_cpu[i]
        assert orig == filtered_element, f"Mismatching intersecting element at index {i}, expected {orig} and got {filtered_element}"


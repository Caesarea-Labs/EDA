
import random
from .geometry.geometry import Point2D, Polygon2D, Triangle2D
from .geometry.geometry_utils import triangulate_polygon


def sample_random_point(polygon: Polygon2D) -> Point2D:
    """
    Returns a random point within the polygon. Every point has an equal chance of being chosen.
    """

    # 1. Split into triangles
    triangulated = triangulate_polygon(polygon).resolve_triangles()

    # 2. Compute total area of triangles to know the relative size of each triangle
    triangle_areas = [t.area() for t in triangulated]
    total_area = sum(triangle_areas)
    # 3. Compute the relative area of each triangle. This is the weight of each triangle - the chance of it being chosen.
    relative_triangle_areas = [area / total_area for area in triangle_areas]

    # 4. Choose a random triangle, given the weights - larger triangle have a higher chance of being chosen as they "contain more points".
    random_triangle = random.choices(triangulated, weights=relative_triangle_areas, k=1)[0]

    return sample_random_triangle_point(random_triangle)


def sample_random_triangle_point(triangle: Triangle2D) -> Point2D:
    # Generate two random numbers for barycentric coordinates
    r1 = random.random()
    r2 = random.random()

    # Adjust r1 and r2 if their sum is greater than 1
    if r1 + r2 > 1:
        r1 = 1 - r1
        r2 = 1 - r2

    # Calculate the third barycentric coordinate
    r3 = 1 - r1 - r2

    # Compute the random point using the barycentric coordinates
    x = r3 * triangle.a.x + r1 * triangle.b.x + r2 * triangle.c.x
    y = r3 * triangle.a.y + r1 * triangle.b.y + r2 * triangle.c.y

    return Point2D(x, y)

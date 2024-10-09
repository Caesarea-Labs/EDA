from gdstk import Polygon
import gdstk
import shapely
from .geometry.geometry import Polygon2D
from .utils import max_of, measure_time, min_of, none_check

GdsPolygonBB = tuple[tuple[float, float], tuple[float, float]]


@measure_time
def get_contained_rectangles(rectangles: list[GdsPolygonBB],
                             bounding_box: Polygon2D, exclusive: bool) -> list[int]:
    """
    Returns the indices of rectangles that exist inside the passed bounding box.
    If exclusive is true, returns only rectangles that are entirely in the bounding box.
    If exclusive is false, return rectangles that only intersect with the bounding box as well.
    """
    # (bbox_x_min, bbox_y_min), (bbox_x_max, bbox_y_max) = bounding_box
    bbox_x_min = min_of(bounding_box, key=lambda bb: bb.x)
    bbox_y_min = min_of(bounding_box, key=lambda bb: bb.y)
    bbox_x_max = max_of(bounding_box, key=lambda bb: bb.x)
    bbox_y_max = max_of(bounding_box, key=lambda bb: bb.y)
    shapely_bounding_box = shapely.Polygon(bounding_box)
    shapely.prepare(shapely_bounding_box)

    def is_point_in_polygon(point: tuple[float, float], polygon: list[tuple[float, float]]) -> bool:
        """
        Determines if a point is inside a polygon using the ray-casting algorithm.

        :param point: A tuple representing the coordinates (x, y) of the point.
        :param polygon: A list of tuples representing the vertices of the polygon.
        :return: True if the point is inside the polygon, False otherwise.
        """
        # Extract the x and y coordinates of the point
        px, py = point

        # Number of vertices in the polygon
        num_vertices = len(polygon)

        # Initialize a flag to keep track of whether the point is inside the polygon
        inside = False

        # Get the coordinates of the first vertex
        x1, y1 = polygon[0]

        # Loop through each edge of the polygon
        for i in range(1, num_vertices + 1):
            # Get the coordinates of the next vertex
            x2, y2 = polygon[i % num_vertices]

            # Check if the point lies within the y-coordinates of the current polygon edge
            if py >= min(y1, y2):
                if py <= max(y1, y2):
                    # Check if the point lies to the left of the polygon edge
                    if px <= max(x1, x2):
                        # Skip horizontal edges (no intersection for ray-casting method)
                        if y1 != y2:
                            # Compute the x-coordinate of the intersection between the polygon edge and a horizontal line through the point
                            x_intersection = (py - y1) * (x2 - x1) / (y2 - y1) + x1
                            if x1 == x2 or px <= x_intersection:
                                # Toggle the inside flag whenever an intersection is found
                                inside = not inside

            # Move to the next edge
            x1, y1 = x2, y2

        return inside
    # Function to check if a rectangle is entirely contained in a polygon

    def is_rectangle_entirely_in_bounding_box(rect: tuple[tuple[float, float], tuple[float, float]]) -> bool:
        # Extract rectangle corner points
        (x1, y1), (x2, y2) = rect
        rect_corners = [
            (x1, y1),  # bottom-left
            (x1, y2),  # top-left
            (x2, y2),  # top-right
            (x2, y1)   # bottom-right
        ]

        # Check if all rectangle corners are inside the polygon.
        # If want to check for any intersection, even if not fully contained.
        return all(is_point_in_polygon(corner, [bounding_box[0].to_tuple(), bounding_box[1].to_tuple()]) for corner in rect_corners)

    def rectangle_contained(rect: GdsPolygonBB) -> bool:
        (rect_x_min, rect_y_min), (rect_x_max, rect_y_max) = rect

        # First, do a very fast check - does the rectangle exist inside the bounding box of the polygon? if not, it has no chance of being contained
        # inside the polygon, which is smaller than its bounding box.

        if exclusive:
            if rect_x_max > bbox_x_max or rect_x_min < bbox_x_min or rect_y_max > bbox_y_max or rect_y_min < bbox_y_min:
                return False
            # Second - do a slow ray-casting check on the few rectangle that are actually someone in this zone.
            return is_rectangle_entirely_in_bounding_box(rect)
            #         # If we want to check for any intersection, even if not fully contained,
        # we need to replace rect_x_max with rect_x_min, rect_x_min with rect_x_max, and the same with the y values.
        elif rect_x_min > bbox_x_max or rect_x_max < bbox_x_min or rect_y_min > bbox_y_max or rect_y_max < bbox_y_min:
            return False
        else:
            shapely_rect = shapely.box(rect[0][0], rect[0][1], rect[1][0], rect[1][1])
            # If we want normal intersection and the bounding box is in the area, use the shapely algorithm.
            return shapely.intersects(shapely_bounding_box, shapely_rect)

    result = []
    for i, rect in enumerate(rectangles):
        if i % 100000 == 0:
            print(f"checking rect {i}")
        if rectangle_contained(rect):
            result.append(i)

    return result


def cut_polygons(polygons: list[Polygon], cut_shape: Polygon2D) -> list[gdstk.Polygon]:
    """
    Returns the intersecting part of the polygons with the cut shape
    """
    shapely_cut = shapely.Polygon([(p.x, p.y) for p in cut_shape])
    shapely.prepare(shapely_cut)
    return [polygon for cut_part in polygons for polygon in cut_polygon(cut_part, shapely_cut)]


def cut_polygon(polygon: gdstk.Polygon, cut_shape: shapely.Polygon) -> list[gdstk.Polygon]:
    """
    Returns the intersection of the polygon and the cut shape. May be multiple polygons. 
    """
    # Convert GDSTK polygon to Shapely polygon
    gdstk_points = polygon.points
    shapely_polygon = shapely.Polygon(gdstk_points)

    # Perform the intersection
    intersection = shapely.intersection(cut_shape, shapely_polygon)

    # We don't need polygons that intersect so little that the intersection is one dimensional
    if intersection.is_empty or isinstance(intersection, shapely.LineString): return []

    # assert not intersection.is_empty, f"Expected polygons {polygon} and {cut_shape} to intersect before cutting them"

    if isinstance(intersection, shapely.Polygon):
        geoms = [intersection]
    elif  isinstance(intersection, shapely.MultiPolygon):
        geoms = intersection.geoms
    elif isinstance(intersection, shapely.GeometryCollection):
        geoms =intersection.geoms
    else:
         assert False, f"Unexpected type as result of intersection of polygons {shapely_polygon} and {cut_shape}: {intersection}"

    # any

    return [
        gdstk.Polygon(list(geom.exterior.coords), layer=polygon.layer, datatype=polygon.datatype) for geom in geoms 
        # We don't need polygons that intersect so little that the intersection is one dimensional
        if not isinstance(geom, shapely.LineString)
    ]

    # x = geoms
    # for y in x:
    #     y.exterior.coords

    # geoms = [intersection] if isinstance(intersection, shapely.Polygon) else \
    #         intersection.geoms if else \
            

    # Check if the intersection is a polygon
    # if isinstance(intersection, shapely.Polygon):
    #     # Convert back to GDSTK polygon
    #     new_points = list(intersection.exterior.coords)
    #     return [gdstk_polygon(new_points)]

    # # If the intersection is a MultiPolygon, return the largest part
    # elif isinstance(intersection, shapely.MultiPolygon):
    #     # return [
    #     #     gdstk_polygon(part.exterior.coords) for part in intersection.geoms
    #     # ]
    #     largest = max(intersection.geoms, key=lambda x: x.area)
    #     new_points = list(largest.exterior.coords)
    #     return gdstk.Polygon(new_points, layer=polygon.layer, datatype=polygon.datatype)

    # # If the intersection is neither a Polygon nor a MultiPolygon, return None
    # else:
    #     assert False, f"Expected the intersection of polygons {shapely_polygon} and {cut_shape} to be a polygon"

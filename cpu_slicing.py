from gpu_slicing import GdsPolygonBB
from utils import measure_time

@measure_time
def get_contained_rectangles(rectangles: list[GdsPolygonBB], 
                                   bounding_box: list[tuple[int, int]], ) -> list[int]:
    """
    Returns the indices of rectangles that exist entirely inside the passed bounding box.

    """
    # (bbox_x_min, bbox_y_min), (bbox_x_max, bbox_y_max) = bounding_box
    bbox_x_min = min(bounding_box, key=lambda bb: bb[0])[0]
    bbox_y_min = min(bounding_box, key=lambda bb: bb[1])[1]
    bbox_x_max = max(bounding_box, key=lambda bb: bb[0])[0]
    bbox_y_max = max(bounding_box, key=lambda bb: bb[1])[1]

    def is_point_in_polygon(point: tuple[float, float], polygon: list[tuple[int, int]]) -> bool:
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
    def is_rectangle_in_polygon(rect: tuple[tuple[float, float], tuple[float, float]], 
                                bounding_box: list[tuple[int, int]]) -> bool:
        # Extract rectangle corner points
        (x1, y1), (x2, y2) = rect
        rect_corners = [
            (x1, y1),  # bottom-left
            (x1, y2),  # top-left
            (x2, y2),  # top-right
            (x2, y1)   # bottom-right
        ]

        # Check if all rectangle corners are inside the polygon.
        # If want to check for any intersection, even if not fully contained, this can be any() instead of all(). 
        return all(is_point_in_polygon(corner, bounding_box) for corner in rect_corners)


    def rectangle_contained(rect: GdsPolygonBB):
        (rect_x_min, rect_y_min), (rect_x_max, rect_y_max) = rect

        # First, do a very fast check - does the rectangle exist inside the bounding box of the polygon? if not, it has no chance of being contained
        # inside the polygon, which is smaller than its bounding box.
        # If we want to check for any intersection, even if not fully contained, 
        # we need to replace rect_x_max with rect_x_min, rect_x_min with rect_x_max, and the same with the y values.
        if rect_x_max > bbox_x_max or rect_x_min < bbox_x_min or rect_y_max > bbox_y_max or rect_y_min < bbox_y_min:
            return False
        # Second - do a slow ray-casting check on the few rectangle that are actually someone in this zone. 
        return is_rectangle_in_polygon(rect, bounding_box)
    
    result = []
    for i, rect in enumerate(rectangles):
        if i % 100000 == 0:
            print(f"checking rect {i}")
        if rectangle_contained(rect):
            result.append(i)

    return result

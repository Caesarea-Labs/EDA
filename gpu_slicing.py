# from typing import Any, Tuple, TypeAlias
# import numpy as np
# import cupy as cp
# from numpy.typing import NDArray

# from utils import measure_time

# # ((min_x,min_y), (max_x, max_y))

# @measure_time
# def filter_intersecting_rectangles_gpu(rectangles:  list[GdsPolygonBB], bounding_box: GdsPolygonBB) -> list[int]:
#     """
#     Filters rectangles that intersect with the given bounding box using GPU acceleration.

#     Parameters:
#         rectangles (np.ndarray): Array of shape (N, 4), where each row is (x_min, y_min, x_max, y_max).
#         bounding_box (tuple or list): (x_min, y_min, x_max, y_max).

#     Returns:
#         np.ndarray: Filtered array of rectangles that intersect with the bounding box.
#     """

#     # Transfer data to GPU
#     rectangles_as_2d_array = [(r[0][0], r[0][1], r[1][0], r[1][1]) for r in rectangles]
#     d_rects = cp.array(rectangles_as_2d_array, dtype=cp.float32)  # Shape: (N, 4)
#     d_bbox = cp.asarray([bounding_box[0][0], bounding_box[0][1], bounding_box[1][0], bounding_box[1][1]])  # Shape: (4,)

#     # Extract bounding box coordinates
#     bbox_x_min, bbox_y_min, bbox_x_max, bbox_y_max = d_bbox

#     # Extract rectangle coordinates
#     rect_x_min = d_rects[:, 0]
#     rect_y_min = d_rects[:, 1]
#     rect_x_max = d_rects[:, 2]
#     rect_y_max = d_rects[:, 3]

#     # Compute intersection mask
#     mask = (
#         (rect_x_min <= bbox_x_max) &
#         (rect_x_max >= bbox_x_min) &
#         (rect_y_min <= bbox_y_max) &
#         (rect_y_max >= bbox_y_min)
#     )

#     # Get the indices where mask is True
#     intersecting_indices = cp.where(mask)[0]

#     # Transfer the indices back to CPU and convert to a Python list
#     return intersecting_indices.get().tolist()






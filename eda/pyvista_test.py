# import pyvista as pv
# import numpy as np

# def create_mesh(points, triangles):
#     """
#     Create and plot a mesh from points and triangles.

#     Args:
#     points: A list or numpy array of 3D points (vertices) where each point is a list or tuple of 3 coordinates [x, y, z].
#     triangles: A list of triangles, where each triangle is a list of 3 point indices [p1, p2, p3].
#     """
#     # Convert the points and triangles to numpy arrays
#     points = np.array(points)
#     triangles = np.array(triangles)
    
#     # Convert the triangles into the format required by PyVista
#     faces = np.hstack([np.full((triangles.shape[0], 1), 3), triangles]).astype(np.int32)
    
#     # Create the PolyData mesh
#     mesh = pv.PolyData(points, faces)
    
#     # Plot the mesh
#     plotter = pv.Plotter()
#     plotter.add_mesh(mesh, show_edges=False, color="lightblue")
#     plotter.show()

# # Example: Create a mesh with 4 points and 2 triangles (a simple square composed of two triangles)
# points = [
#     [0, 0, 0],   # Point 0
#     [1, 0, 0],   # Point 1
#     [1, 1, 0],   # Point 2
#     [0, 1, 0]    # Point 3
# ]

# # Define the two triangles using the indices of the points
# triangles = [
#     [0, 1, 2],  # Triangle 1
#     [0, 2, 3]   # Triangle 2
# ]

# # Create and plot the mesh
# create_mesh(points, triangles)
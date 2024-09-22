import pyvista as pv
import numpy as np

def extrude_polygon(vertices, extrude_length=1.0):
    """
    Extrude a 2D polygon into 3D space.

    Parameters:
    - vertices: List of (x, y) tuples defining the 2D polygon.
    - extrude_length: The length to extrude the polygon along the z-axis.

    Returns:
    - A PyVista mesh of the extruded polygon.
    """
    # Convert vertices to a numpy array and add z=0 coordinate
    points = np.array([(x, y, 0) for x, y in vertices])

    # Define the face: the first number is the number of points in the face
    N = len(vertices)
    faces = np.hstack([[N] + list(range(N))])

    # Create the PolyData object
    polygon = pv.PolyData(points, faces)

    # Extrude the polygon along the z-axis
    extruded = polygon.extrude((0, 0, extrude_length), cappin)

    # Plot the extruded polygon
    plotter = pv.Plotter()
    plotter.add_mesh(extruded, color='lightblue', show_edges=True)
    plotter.show_grid()
    plotter.show()

    return extruded

# Define the vertices of the Tetris S shape in 2D
tetris_s_vertices = [
    (0, 0), (2, 0), (2, 1),
    (3, 1), (3, 3), (1, 3),
    (1, 2), (0, 2)
]

# Close the polygon by ensuring the last vertex connects to the first
tetris_s_vertices.append(tetris_s_vertices[0])

# Extrude the Tetris S shape
extruded_shape = extrude_polygon(tetris_s_vertices, extrude_length=1.0)

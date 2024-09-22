import triangle
import matplotlib.pyplot as plt

# Define the S-shaped polygon vertices
vertices = {
    'vertices': [
        (0, 0),  # Bottom-left corner
        (2, 0),  # Bottom-right corner
        (2, 1),  # Middle-right corner
        (3, 1),  # Middle-right overhang
        (3, 2),  # Top-right overhang
        (1, 2),  # Top-left corner of overhang
        (1, 1),  # Middle-left corner
        (0, 1)   # Back to bottom-left corner
    ],
    'segments': [
        [0, 1],  # Bottom edge
        [1, 2],  # Right vertical edge
        [2, 3],  # Middle-right edge
        [3, 4],  # Right-top overhang
        [4, 5],  # Top overhang
        [5, 6],  # Left-top overhang
        [6, 7],  # Middle-left edge
        [7, 0]   # Back to bottom-left edge
    ]
}

# Compute the Constrained Delaunay Triangulation
triangulation = triangle.triangulate(vertices, 'p')

# Plot the triangulation
plt.triplot(triangulation['vertices'][:, 0], triangulation['vertices'][:, 1], triangulation['triangles'])
plt.plot(vertices['vertices'][0][0], vertices['vertices'][0][1], 'ro')  # highlight a vertex
plt.show()

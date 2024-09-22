import plotly.graph_objects as go
import numpy as np
from shapely import Polygon, delaunay_triangles

# Define the vertices of the L shape
vertices = np.array([
    [0, 0, 0],  # vertex 0
    [1, 0, 0],  # vertex 1
    [1, 2, 0],  # vertex 2
    [2, 2, 0],  # vertex 3
    [2, 3, 0],  # vertex 4
    [0, 3, 0],  # vertex 5
])

# Extend the vertices along the Z-axis by 2 units (extruding the L-shape)
vertices = np.vstack([vertices, vertices + [0, 0, 2]])

# Define the faces of the extruded L-shape, split each quadrilateral into two triangles
triangles = [
    # Bottom face
    [0, 1, 2], [0, 2, 5],
    [2, 3, 4], [2, 4, 5],

    # Top face (extruded)
    [6, 7, 8], [6, 8, 11],
    [8, 9, 10], [8, 10, 11],

    # Side faces (extrusion sides)
    [0, 1, 7], [0, 7, 6],  # side between vertices 0, 1, 7, 6
    [1, 2, 8], [1, 8, 7],  # side between vertices 1, 2, 8, 7
    [2, 3, 9], [2, 9, 8],  # side between vertices 2, 3, 9, 8
    [3, 4, 10], [3, 10, 9],  # side between vertices 3, 4, 10, 9
    [4, 5, 11], [4, 11, 10],  # side between vertices 4, 5, 11, 10
    [5, 0, 6], [5, 6, 11]   # side between vertices 5, 0, 6, 11
]

# Extract x, y, z coordinates
x = vertices[:, 0]
y = vertices[:, 1]
z = vertices[:, 2]

# Create the mesh trace to fill the sides with color using triangles
mesh = go.Mesh3d(
    x=x,
    y=y,
    z=z,
    i=[triangle[0] for triangle in triangles],
    j=[triangle[1] for triangle in triangles],
    k=[triangle[2] for triangle in triangles],
    color='lightblue',
    opacity=1.0
)

# Create traces for the wireframe edges
traces = []
edges = [
    [0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0],  # bottom L-shape
    [6, 7], [7, 8], [8, 9], [9, 10], [10, 11], [11, 6],  # top L-shape (extruded)
    [0, 6], [1, 7], [2, 8], [3, 9], [4, 10], [5, 11]  # vertical edges (extrusion)
]

for edge in edges:
    ex = [x[edge[0]], x[edge[1]]]
    ey = [y[edge[0]], y[edge[1]]]
    ez = [z[edge[0]], z[edge[1]]]
    traces.append(go.Scatter3d(x=ex, y=ey, z=ez, mode='lines', line=dict(color='blue', width=2)))

# Create the layout
layout = go.Layout(
    scene=dict(
        xaxis=dict(title='X'),
        yaxis=dict(title='Y'),
        zaxis=dict(title='Z'),
        aspectmode='data'
    ),
    title='3D Extruded L-Shape with Filled Sides (Using Triangles)'
)

# Create the figure and show it
fig = go.Figure(data=[mesh] + traces, layout=layout)
fig.show()



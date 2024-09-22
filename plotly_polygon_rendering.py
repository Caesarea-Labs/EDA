from dataclasses import dataclass
import plotly.graph_objects as go
import numpy as np
from shapely import Polygon, delaunay_triangles

from layout import Point2D
from polygon_to_mesh import Mesh, Polygon3D, polygon_to_mesh

def mesh_text(mesh: Mesh) -> go.Scatter3d:
    x_coords = [point.x for point in mesh.vertices]
    y_coords = [point.y for point in mesh.vertices]
    z_coords = [point.z for point in mesh.vertices]

    # Add the name text
    center_x = sum(x_coords) / len(x_coords)
    center_y = sum(y_coords) / len(y_coords)
    center_z =sum(z_coords) / len(z_coords)
    return go.Scatter3d(
        x=[center_x], y=[center_y], z=[center_z],
        mode='text',
        text=[mesh.name],
        textposition='middle center'
    )

def to_plotly_mesh(mesh: Mesh) -> go.Mesh3d:
    # Extract x, y, z coordinates
    x = [vertex.x for vertex in mesh.vertices]
    y = [vertex.y for vertex in mesh.vertices]
    z = [vertex.z for vertex in mesh.vertices]

    a_indices = [triangle.a_index for triangle in mesh.triangles]
    b_indices = [triangle.b_index for triangle in mesh.triangles]
    c_indices = [triangle.c_index for triangle in mesh.triangles]

    # Create the mesh trace to fill the sides with color using triangles
    return go.Mesh3d(
        x=x,
        y=y,
        z=z,
        i=a_indices,
        j=b_indices,
        k=c_indices,
        color=mesh.color,
        opacity=mesh.alpha
    )


def plotly_plot_mesh(mesh: Mesh):

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
    fig = go.Figure(data=[to_plotly_mesh(mesh), mesh_text(mesh)]  # + traces
                    , layout=layout)
    fig.show()




polygon = Polygon3D(
    z_base=0, z_top=1,
    vertices=[
        Point2D(0, 0),  # Bottom-left corner
        Point2D(2, 0),  # Bottom-right corner
        Point2D(2, 1),  # Middle-right corner
        Point2D(3, 1),  # Middle-right overhang
        Point2D(3, 2),  # Top-right overhang
        Point2D(1, 2),  # Top-left corner of overhang
        Point2D(1, 1),  # Middle-left corner
        Point2D(0, 1)   # Back to bottom-left corner
    ],
    color="blue", alpha=0.3, name="test"
)

plotly_plot_mesh(
    polygon_to_mesh(polygon)
)

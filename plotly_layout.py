from dataclasses import dataclass
import plotly.graph_objects as go
import numpy as np
from pyparsing import col
from shapely import Polygon, delaunay_triangles

from layout import Layout, Point2D
from polygon_to_mesh import Mesh, ExtrudedPolygon, polygon_to_mesh
from utils import none_check


def mesh_text(mesh: Mesh) -> go.Scatter3d:
    x_coords = [point.x for point in mesh.vertices]
    y_coords = [point.y for point in mesh.vertices]
    z_coords = [point.z for point in mesh.vertices]

    # Add the name text
    center_x = sum(x_coords) / len(x_coords)
    center_y = sum(y_coords) / len(y_coords)
    center_z = sum(z_coords) / len(z_coords)
    return go.Scatter3d(
        x=[center_x], y=[center_y], z=[center_z],
        mode='text',
        text=[mesh.name],
        textposition='middle center',
        name=mesh.name,
        legendgroup=mesh.name,
        showlegend=False
    )


def to_plotly_mesh(mesh: Mesh, showing_text: bool) -> go.Mesh3d:
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
        opacity=mesh.alpha,
        legendgroup=mesh.name,
        showlegend=showing_text
    )


def plotly_plot_meshes(title: str, meshes: list[Mesh], show_text: bool):

    # Create the layout
    layout = go.Layout(
        scene=dict(
            xaxis=dict(title='X'),
            yaxis=dict(title='Y'),
            zaxis=dict(title='Z'),
            aspectmode='data'
        ),
        title=title,
    )

    data = []

    for mesh in meshes:
        data.append(to_plotly_mesh(mesh, showing_text=show_text))

    if show_text:
        for mesh in meshes:
            data.append(mesh_text(mesh))
    
    # Create the figure and show it
    fig = go.Figure(data=data, layout=layout)
    fig.show()


fill_colors = ['cyan', 'lightgreen', 'lightblue', 'orange', 'yellow',
               'pink', 'lightcoral', 'lightgray', 'lavender', 'beige']


def plotly_plot_layout(layout: Layout, show_text: bool):
    """
    Will draw the layout in 3D.
    If show_text is true, every metal and via will have its named displayed. This should be turned off for large layouts. 
    """
    meshes = []

    for metal in layout.metals:
        polygon = ExtrudedPolygon(
            z_base=none_check(metal.layer) - 0.25,
            z_top=none_check(metal.layer) + 0.25,
            color=fill_colors[none_check(metal.signal_index) % len(fill_colors)],
            # edge_color=edge_colors[metal.signal_index % len(edge_colors)],
            vertices=metal.vertices,
            alpha=0.5,
            name=metal.name
        )
        meshes.append(polygon_to_mesh(polygon))

    for via in layout.vias:
        polygon = ExtrudedPolygon(
            z_base=none_check(via.layer),
            z_top=none_check(via.layer) + 1,
            color="black",
            vertices=via.rect.vertices(),
            alpha=0.3,
            name=via.name
        )
        meshes.append(polygon_to_mesh(polygon))


    # Convert polygons to meshes
    plotly_plot_meshes("Layout", meshes, show_text)


if __name__ == "__main__":
    polygon_1 = ExtrudedPolygon(
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
        color="blue", alpha=0.3, name="test1"
    )

    polygon_2 = ExtrudedPolygon(
        z_base=10, z_top=11,
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
        color="blue", alpha=0.3, name="test2"
    )

    plotly_plot_meshes(
        "Layout",
        [
            polygon_to_mesh(polygon_1),
            polygon_to_mesh(polygon_2),
        ],
        show_text=True
    )

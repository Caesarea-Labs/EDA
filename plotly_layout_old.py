from Draw import Polygon3D
from layout import Layout
import plotly.graph_objects as go
import numpy as np

from utils import max_of, min_of, none_check

fill_colors = ['cyan', 'lightgreen', 'lightblue', 'orange', 'yellow',
               'pink', 'lightcoral', 'lightgray', 'lavender', 'beige']

edge_colors = ['red', 'blue', 'green', 'purple', 'black',
               'brown', 'darkblue', 'darkgreen', 'darkred', 'darkorange']

def plot_layout_plotly(layout: Layout):
    fig = go.Figure()

    max_z = max_of(layout.metals, key=lambda m: none_check(m.layer))
    max_xy = max_of(layout.metals, key=lambda m: max_of(m.vertices, key=lambda v: max(v.x, v.y)))
    min_xy = min_of(layout.metals, key=lambda m: min_of(m.vertices, key=lambda v: min(v.x, v.y)))

    def draw_shape(shape: Polygon3D):
        x_coords = [point.x for point in shape.vertices]
        y_coords = [point.y for point in shape.vertices]

        # Create the base
        # fig.add_trace(go.Mesh3d(
        #     x=x_coords, y=y_coords, z=[shape.z_base]*len(x_coords),
        #     i=[0]*(len(x_coords)-2), j=list(range(1, len(x_coords)-1)), k=list(range(2, len(x_coords))),
        #     color=shape.fill_color, opacity=shape.alpha, name=shape.name
        # ))

        # Create the top
        # fig.add_trace(go.Mesh3d(
        #     x=x_coords, y=y_coords, z=[shape.z_top]*len(x_coords),
        #     i=[0]*(len(x_coords)-2), j=list(range(1, len(x_coords)-1)), k=list(range(2, len(x_coords))),
        #     color=shape.fill_color, opacity=shape.alpha, name=shape.name
        # ))

        # Create the sides
        for i in range(len(x_coords)):
            next_i = (i + 1) % len(x_coords)
            fig.add_trace(go.Mesh3d(
                x=[x_coords[i], x_coords[next_i], x_coords[next_i], x_coords[i]],
                y=[y_coords[i], y_coords[next_i], y_coords[next_i], y_coords[i]],
                z=[shape.z_base, shape.z_base, shape.z_top, shape.z_top],
                i=[0], j=[1], k=[2],
                color=shape.fill_color, opacity=shape.alpha, name=shape.name
            ))

        # Add the name text
        center_x = sum(x_coords) / len(x_coords)
        center_y = sum(y_coords) / len(y_coords)
        center_z = (shape.z_base + shape.z_top) / 2
        fig.add_trace(go.Scatter3d(
            x=[center_x], y=[center_y], z=[center_z],
            mode='text',
            text=[shape.name],
            textposition='middle center'
        ))

    for metal in layout.metals:
        assert metal.layer is not None, "layer must be set to draw metal"
        assert metal.signal_index is not None, "signal index must be set to draw metal"
        polygon = Polygon3D(
            z_base=metal.layer - 0.25,
            z_top=metal.layer + 0.25,
            fill_color=fill_colors[metal.signal_index % len(fill_colors)],
            edge_color=edge_colors[metal.signal_index % len(edge_colors)],
            vertices=metal.vertices,
            alpha=0.5,
            name=metal.name
        )
        draw_shape(polygon)

    for via in layout.vias:
        assert via.layer is not None, "layer must be set to draw via"
        polygon = Polygon3D(
            z_base=via.layer,
            z_top=via.layer + 1,
            fill_color="black",
            edge_color="white",
            vertices=via.rect.vertices(),
            alpha=0.3,
            name=via.name
        )
        draw_shape(polygon)

    fig.update_layout(
        scene=dict(
            xaxis_title='X',
            yaxis_title='Y',
            zaxis_title='Z',
            xaxis=dict(range=[min_xy, max_xy]),
            yaxis=dict(range=[min_xy, max_xy]),
            zaxis=dict(range=[0, max_z])
        ),
        title='3D Shape Layout',
        autosize=False,
        width=800,
        height=800,
        margin=dict(l=65, r=50, b=65, t=90)
    )

    fig.show()